"""Pydantic schemas for request and response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import date


class QuestionRequest(BaseModel):
    """Request schema for the /ask endpoint."""
    question: str = Field(..., min_length=1, description="Natural language question about sales data")


class QuestionResponse(BaseModel):
    """Response schema for the /ask endpoint."""
    success: bool
    question: str
    intent: Optional[str] = None
    answer: str
    data: Optional[Dict[str, Any]] = None
    explanation: str
    limitations: List[str] = []
    source: str = "database"


class HealthResponse(BaseModel):
    """Response schema for the /health endpoint."""
    status: str
    database_available: bool
    record_count: int


class MetadataResponse(BaseModel):
    """Response schema for the /metadata endpoint."""
    record_count: int
    date_range: Optional[Dict[str, str]] = None
    products: List[str]
    regions: List[str]
    import_status: str


class TotalRevenueResponse(BaseModel):
    """Response schema for total revenue."""
    total_revenue: float
    currency: str = ""
    transaction_count: int
    explanation: str


class TopProductResponse(BaseModel):
    """Response schema for highest-revenue product."""
    product: str
    total_revenue: float
    currency: str = ""
    all_products: List[Dict[str, Any]]
    explanation: str


class MonthlyRevenueResponse(BaseModel):
    """Response schema for monthly revenue trend."""
    monthly_data: List[Dict[str, Any]]
    date_range: Dict[str, str]
    explanation: str


class TopRegionResponse(BaseModel):
    """Response schema for highest-sales region."""
    region: str
    total_revenue: float
    currency: str = ""
    all_regions: List[Dict[str, Any]]
    explanation: str


class RevenueComparisonRequest(BaseModel):
    """Request schema for revenue comparison."""
    month1: int = Field(..., ge=1, le=12, description="First month (1-12)")
    year1: int = Field(..., ge=2000, le=2100, description="First year")
    month2: int = Field(..., ge=1, le=12, description="Second month (1-12)")
    year2: int = Field(..., ge=2000, le=2100, description="Second year")


class RevenueComparisonResponse(BaseModel):
    """Response schema for revenue comparison."""
    month1_revenue: float
    month2_revenue: float
    absolute_change: float
    percentage_change: Optional[float]
    trend: str
    explanation: str


class ColumnMapping(BaseModel):
    """Schema for CSV column mapping."""
    transaction_id: str
    transaction_date: str
    product: str
    category: Optional[str] = None
    region: str
    sales_channel: Optional[str] = None
    quantity: Optional[str] = None
    unit_price: Optional[str] = None
    discount_amount: Optional[str] = None
    status: Optional[str] = None
