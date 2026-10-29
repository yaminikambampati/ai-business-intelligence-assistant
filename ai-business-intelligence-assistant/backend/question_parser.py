"""Question parser for natural language intent detection."""
import re
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class DeterministicParser:
    """Deterministic parser for common question patterns."""

    # Intent patterns
    PATTERNS = {
        "total_revenue": [
            r"total revenue",
            r"total sales",
            r"overall revenue",
            r"calculate revenue",
            r"sum of revenue",
            r"what is the revenue"
        ],
        "top_product": [
            r"highest revenue product",
            r"product generated the highest revenue",
            r"which product made the most money",
            r"top product",
            r"best selling product",
            r"product with most revenue",
            r"product has the highest sales",
            r"made the most money"
        ],
        "monthly_revenue": [
            r"monthly revenue trend",
            r"revenue month by month",
            r"monthly sales",
            r"revenue by month",
            r"show revenue month"
        ],
        "top_region": [
            r"highest sales region",
            r"region generated the highest sales",
            r"which region performed best",
            r"top region",
            r"best region",
            r"region with most revenue",
            r"region has the highest sales",
            r"region has the most sales",
            r"highest sales"
        ],
        "revenue_comparison": [
            r"revenue change between",
            r"compare revenue",
            r"how did revenue change",
            r"revenue difference",
            r"compare.*month"
        ]
    }

    @classmethod
    def parse(cls, question: str) -> Dict[str, Any]:
        """
        Parse a natural language question and extract intent.

        Args:
            question: The user's question

        Returns:
            Dictionary with intent, parameters, and metadata
        """
        question_lower = question.lower().strip()

        # Try to match each intent pattern
        for intent, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    result = {
                        "intent": intent,
                        "parameters": cls._extract_parameters(intent, question),
                        "requires_clarification": False,
                        "confidence": "high"
                    }
                    logger.info(f"Deterministic parser matched intent: {intent}")
                    return result

        # If no pattern matched, return unsupported
        return {
            "intent": "unsupported",
            "parameters": {},
            "requires_clarification": True,
            "confidence": "low",
            "message": "Question not recognized. Please ask about total revenue, top product, monthly revenue, top region, or revenue comparison between months."
        }

    @classmethod
    def _extract_parameters(cls, intent: str, question: str) -> Dict[str, Any]:
        """Extract parameters based on intent."""
        parameters = {}

        if intent == "revenue_comparison":
            # Extract months and years
            # Patterns: "January 2025", "Jan 2025", "2025-01", "January"
            months = {
                "january": 1, "jan": 1, "february": 2, "feb": 2,
                "march": 3, "mar": 3, "april": 4, "apr": 4,
                "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
                "august": 8, "aug": 8, "september": 9, "sep": 9,
                "october": 10, "oct": 10, "november": 11, "nov": 11,
                "december": 12, "dec": 12
            }

            question_lower = question.lower()

            # Find month names in order of appearance
            found_months = []
            for month_name, month_num in months.items():
                # Find position of month name in question
                pos = question_lower.find(month_name)
                if pos != -1:
                    found_months.append((pos, month_name, month_num))

            # Sort by position to maintain order
            found_months.sort(key=lambda x: x[0])

            # Find all years (4-digit numbers) in order
            years = re.findall(r"\b(20\d{2})\b", question)

            # Try to extract YYYY-MM format
            year_month_pattern = re.findall(r"(\d{4})-(\d{1,2})", question)
            if year_month_pattern:
                for y, m in year_month_pattern:
                    if y not in years:
                        years.append(y)
                    found_months.append((999, f"month-{m}", int(m)))

            # Sort again to include any YYYY-MM patterns
            found_months.sort(key=lambda x: x[0])

            # Extract unique month numbers in order
            month_numbers = [m[2] for m in found_months]

            if len(month_numbers) >= 2 and len(years) >= 2:
                parameters["month1"] = month_numbers[0]
                parameters["year1"] = int(years[0])
                parameters["month2"] = month_numbers[1]
                parameters["year2"] = int(years[1])
            elif len(month_numbers) >= 2 and len(years) == 1:
                # Same year for both months
                parameters["month1"] = month_numbers[0]
                parameters["year1"] = int(years[0])
                parameters["month2"] = month_numbers[1]
                parameters["year2"] = int(years[0])
            else:
                parameters["requires_clarification"] = True
                parameters["message"] = "Please specify two months and years for comparison, e.g., 'How did revenue change between January 2025 and February 2025?'"

        return parameters


def parse_question(question: str) -> Dict[str, Any]:
    """
    Parse a question using deterministic parsing.

    Args:
        question: The user's question

    Returns:
        Dictionary with intent and parameters
    """
    return DeterministicParser.parse(question)
