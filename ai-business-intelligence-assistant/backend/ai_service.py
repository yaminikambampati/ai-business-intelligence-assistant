"""AI service for optional LLM-based question interpretation."""
from typing import Dict, Any, Optional
import logging
from pydantic import BaseModel, Field

from backend.config import settings

logger = logging.getLogger(__name__)


class IntentResponse(BaseModel):
    """Structured response from LLM for intent detection."""
    intent: str = Field(..., description="The analytical intent: total_revenue, top_product, monthly_revenue, top_region, revenue_comparison, or unsupported")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters")
    requires_clarification: bool = Field(default=False, description="Whether clarification is needed")
    confidence: str = Field(default="medium", description="Confidence level: high, medium, low")
    message: Optional[str] = Field(default=None, description="Additional message if clarification needed")


class AIService:
    """Service for LLM-based question interpretation."""

    def __init__(self):
        self.client = None
        self.model = settings.openai_model
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the OpenAI client if API key is available."""
        if settings.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.warning("OpenAI library not installed")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.info("No OpenAI API key provided, using deterministic parsing only")

    def is_available(self) -> bool:
        """Check if the AI service is available."""
        return self.client is not None

    def parse_question(self, question: str) -> Dict[str, Any]:
        """
        Parse a question using LLM.

        Args:
            question: The user's question

        Returns:
            Dictionary with intent and parameters
        """
        if not self.is_available():
            logger.warning("AI service not available, cannot parse question")
            return {
                "intent": "unsupported",
                "parameters": {},
                "requires_clarification": True,
                "confidence": "low",
                "message": "AI service not available. Please use deterministic question patterns."
            }

        try:
            system_prompt = """You are a question interpreter for a business intelligence application.
Your task is to analyze natural language questions about sales data and extract the analytical intent.

Supported intents:
- total_revenue: Questions asking for total revenue or sales
- top_product: Questions asking which product generated the highest revenue
- monthly_revenue: Questions asking for monthly revenue trends
- top_region: Questions asking which region had the highest sales
- revenue_comparison: Questions comparing revenue between two months
- unsupported: Questions that don't match any supported intent

For revenue_comparison, extract:
- month1: First month (1-12)
- year1: First year (e.g., 2025)
- month2: Second month (1-12)
- year2: Second year (e.g., 2025)

Return a JSON response with this structure:
{
  "intent": "intent_name",
  "parameters": {},
  "requires_clarification": false,
  "confidence": "high|medium|low",
  "message": null
}

If parameters are missing for revenue_comparison, set requires_clarification to true and provide a helpful message."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            parsed = IntentResponse.model_validate_json(content)

            result = parsed.model_dump()
            logger.info(f"AI service parsed intent: {result['intent']}")
            return result

        except Exception as e:
            logger.error(f"Error parsing question with AI: {e}")
            return {
                "intent": "unsupported",
                "parameters": {},
                "requires_clarification": True,
                "confidence": "low",
                "message": f"AI parsing failed: {str(e)}"
            }


# Global AI service instance
ai_service = AIService()
