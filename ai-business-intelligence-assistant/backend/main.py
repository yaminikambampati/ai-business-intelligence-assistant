"""FastAPI main application."""
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

from backend.config import settings
from backend.database import is_database_available, get_record_count
from backend.schemas import (
    QuestionRequest, QuestionResponse, HealthResponse, MetadataResponse,
    TotalRevenueResponse, TopProductResponse, MonthlyRevenueResponse,
    TopRegionResponse, RevenueComparisonRequest, RevenueComparisonResponse
)
from backend.analytics import (
    get_total_revenue, get_top_product, get_monthly_revenue,
    get_top_region, compare_revenue_between_months
)
from backend.question_parser import parse_question
from backend.ai_service import ai_service

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered business intelligence assistant for sales data"
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    db_available = is_database_available()
    record_count = get_record_count()

    return HealthResponse(
        status="healthy" if db_available else "unhealthy",
        database_available=db_available,
        record_count=record_count
    )


@app.get("/metadata", response_model=MetadataResponse)
async def get_metadata():
    """Get dataset metadata."""
    if not is_database_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available or empty"
        )

    from backend.database import get_db

    with get_db() as conn:
        cursor = conn.cursor()

        # Get record count
        cursor.execute("SELECT COUNT(*) as count FROM sales_transactions")
        record_count = cursor.fetchone()["count"]

        # Get date range
        cursor.execute("""
            SELECT MIN(transaction_date) as min_date, MAX(transaction_date) as max_date
            FROM sales_transactions
        """)
        date_range = cursor.fetchone()

        # Get unique products
        cursor.execute("SELECT DISTINCT product FROM sales_transactions ORDER BY product")
        products = [row["product"] for row in cursor.fetchall()]

        # Get unique regions
        cursor.execute("SELECT DISTINCT region FROM sales_transactions ORDER BY region")
        regions = [row["region"] for row in cursor.fetchall()]

    return MetadataResponse(
        record_count=record_count,
        date_range={
            "start": date_range["min_date"],
            "end": date_range["max_date"]
        } if date_range else None,
        products=products,
        regions=regions,
        import_status="completed"
    )


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a natural language question about sales data.

    This endpoint uses either deterministic parsing or optional LLM interpretation
    to understand the question and return answers from the database.
    """
    if not is_database_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available or empty. Please load data first."
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )

    # Try AI service first if available
    if ai_service.is_available():
        logger.info("Using AI service for question parsing")
        parsed = ai_service.parse_question(question)
    else:
        logger.info("Using deterministic parser")
        parsed = parse_question(question)

    intent = parsed.get("intent")
    parameters = parsed.get("parameters", {})

    # Handle unsupported questions
    if intent == "unsupported" or parsed.get("requires_clarification"):
        return QuestionResponse(
            success=False,
            question=question,
            intent=intent,
            answer=parsed.get("message", "Question not recognized. Please ask about total revenue, top product, monthly revenue, top region, or revenue comparison between months."),
            data=None,
            explanation="The question could not be matched to a supported analytical operation.",
            limitations=["Only specific question patterns are supported"],
            source="parser"
        )

    # Route to appropriate analytics function
    try:
        if intent == "total_revenue":
            result = get_total_revenue()
            return QuestionResponse(
                success=True,
                question=question,
                intent=intent,
                answer=f"The total revenue is {result['total_revenue']:.2f}.",
                data=result,
                explanation=result["explanation"],
                limitations=[],
                source="database"
            )

        elif intent == "top_product":
            result = get_top_product()
            return QuestionResponse(
                success=True,
                question=question,
                intent=intent,
                answer=f"The product '{result['product']}' generated the highest revenue of {result['total_revenue']:.2f}.",
                data=result,
                explanation=result["explanation"],
                limitations=[],
                source="database"
            )

        elif intent == "monthly_revenue":
            result = get_monthly_revenue()
            return QuestionResponse(
                success=True,
                question=question,
                intent=intent,
                answer=f"Monthly revenue trend shows data from {result['date_range']['start']} to {result['date_range']['end']}.",
                data=result,
                explanation=result["explanation"],
                limitations=[],
                source="database"
            )

        elif intent == "top_region":
            result = get_top_region()
            return QuestionResponse(
                success=True,
                question=question,
                intent=intent,
                answer=f"The region '{result['region']}' generated the highest revenue of {result['total_revenue']:.2f}.",
                data=result,
                explanation=result["explanation"],
                limitations=[],
                source="database"
            )

        elif intent == "revenue_comparison":
            # Check if parameters are available
            if parameters.get("requires_clarification"):
                return QuestionResponse(
                    success=False,
                    question=question,
                    intent=intent,
                    answer=parameters.get("message", "Please specify two months and years for comparison."),
                    data=None,
                    explanation="Missing required parameters for revenue comparison.",
                    limitations=["Months and years must be specified"],
                    source="parser"
                )

            month1 = parameters.get("month1")
            year1 = parameters.get("year1")
            month2 = parameters.get("month2")
            year2 = parameters.get("year2")

            if None in [month1, year1, month2, year2]:
                return QuestionResponse(
                    success=False,
                    question=question,
                    intent=intent,
                    answer="Please specify two months and years for comparison, e.g., 'How did revenue change between January 2025 and February 2025?'",
                    data=None,
                    explanation="Could not extract month and year parameters from the question.",
                    limitations=["Question must include two months and years"],
                    source="parser"
                )

            result = compare_revenue_between_months(month1, year1, month2, year2)
            return QuestionResponse(
                success=True,
                question=question,
                intent=intent,
                answer=f"Revenue {result['trend']} from the first month to the second month. {result['explanation']}",
                data=result,
                explanation=result["explanation"],
                limitations=[],
                source="database"
            )

        else:
            return QuestionResponse(
                success=False,
                question=question,
                intent=intent,
                answer="Unsupported question type.",
                data=None,
                explanation="The intent was recognized but not implemented.",
                limitations=["This question type is not yet supported"],
                source="parser"
            )

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your question"
        )


@app.get("/analytics/total-revenue", response_model=TotalRevenueResponse)
async def get_total_revenue_endpoint():
    """Get total revenue."""
    if not is_database_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available or empty"
        )

    result = get_total_revenue()
    return TotalRevenueResponse(**result)


@app.get("/analytics/top-product", response_model=TopProductResponse)
async def get_top_product_endpoint():
    """Get the product with highest revenue."""
    if not is_database_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available or empty"
        )

    result = get_top_product()
    return TopProductResponse(**result)


@app.get("/analytics/monthly-revenue", response_model=MonthlyRevenueResponse)
async def get_monthly_revenue_endpoint():
    """Get monthly revenue trend."""
    if not is_database_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available or empty"
        )

    result = get_monthly_revenue()
    return MonthlyRevenueResponse(**result)


@app.get("/analytics/top-region", response_model=TopRegionResponse)
async def get_top_region_endpoint():
    """Get the region with highest revenue."""
    if not is_database_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available or empty"
        )

    result = get_top_region()
    return TopRegionResponse(**result)


@app.get("/analytics/revenue-comparison", response_model=RevenueComparisonResponse)
async def get_revenue_comparison_endpoint(
    month1: int,
    year1: int,
    month2: int,
    year2: int
):
    """Compare revenue between two months."""
    if not is_database_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available or empty"
        )

    result = compare_revenue_between_months(month1, year1, month2, year2)
    return RevenueComparisonResponse(**result)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
