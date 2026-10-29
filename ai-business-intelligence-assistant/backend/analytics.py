"""Analytics service for sales data calculations."""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from backend.database import get_db

logger = logging.getLogger(__name__)


def get_total_revenue() -> Dict[str, Any]:
    """
    Calculate total revenue from all transactions.

    Returns:
        Dictionary with total_revenue, transaction_count, and explanation
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Calculate total revenue
        cursor.execute("""
            SELECT SUM(revenue) as total, COUNT(*) as count
            FROM sales_transactions
            WHERE revenue IS NOT NULL
        """)
        result = cursor.fetchone()

        total_revenue = result["total"] or 0.0
        transaction_count = result["count"] or 0

        return {
            "total_revenue": total_revenue,
            "transaction_count": transaction_count,
            "currency": "",
            "explanation": f"Total revenue calculated from {transaction_count} transactions in the database."
        }


def get_top_product() -> Dict[str, Any]:
    """
    Find the product with the highest total revenue.

    Returns:
        Dictionary with product, total_revenue, all_products, and explanation
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get revenue by product
        cursor.execute("""
            SELECT product, SUM(revenue) as total_revenue, COUNT(*) as transaction_count
            FROM sales_transactions
            WHERE revenue IS NOT NULL
            GROUP BY product
            ORDER BY total_revenue DESC
        """)
        results = cursor.fetchall()

        if not results:
            return {
                "product": None,
                "total_revenue": 0.0,
                "all_products": [],
                "explanation": "No product data available."
            }

        all_products = [
            {
                "product": row["product"],
                "total_revenue": row["total_revenue"] or 0.0,
                "transaction_count": row["transaction_count"]
            }
            for row in results
        ]

        top_product = results[0]

        return {
            "product": top_product["product"],
            "total_revenue": top_product["total_revenue"] or 0.0,
            "all_products": all_products,
            "explanation": f"Product '{top_product['product']}' generated the highest revenue of {top_product['total_revenue']:.2f} from {top_product['transaction_count']} transactions."
        }


def get_monthly_revenue() -> Dict[str, Any]:
    """
    Calculate monthly revenue trend.

    Returns:
        Dictionary with monthly_data, date_range, and explanation
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get monthly revenue
        cursor.execute("""
            SELECT
                strftime('%Y-%m', transaction_date) as month,
                SUM(revenue) as total_revenue,
                COUNT(*) as transaction_count
            FROM sales_transactions
            WHERE revenue IS NOT NULL
            GROUP BY month
            ORDER BY month ASC
        """)
        results = cursor.fetchall()

        # Get date range
        cursor.execute("""
            SELECT MIN(transaction_date) as min_date, MAX(transaction_date) as max_date
            FROM sales_transactions
        """)
        date_range = cursor.fetchone()

        monthly_data = [
            {
                "month": row["month"],
                "total_revenue": row["total_revenue"] or 0.0,
                "transaction_count": row["transaction_count"]
            }
            for row in results
        ]

        return {
            "monthly_data": monthly_data,
            "date_range": {
                "start": date_range["min_date"] if date_range else None,
                "end": date_range["max_date"] if date_range else None
            },
            "explanation": f"Monthly revenue calculated from {len(monthly_data)} months of data."
        }


def get_top_region() -> Dict[str, Any]:
    """
    Find the region with the highest total revenue.

    Returns:
        Dictionary with region, total_revenue, all_regions, and explanation
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get revenue by region
        cursor.execute("""
            SELECT region, SUM(revenue) as total_revenue, COUNT(*) as transaction_count
            FROM sales_transactions
            WHERE revenue IS NOT NULL
            GROUP BY region
            ORDER BY total_revenue DESC
        """)
        results = cursor.fetchall()

        if not results:
            return {
                "region": None,
                "total_revenue": 0.0,
                "all_regions": [],
                "explanation": "No region data available."
            }

        all_regions = [
            {
                "region": row["region"],
                "total_revenue": row["total_revenue"] or 0.0,
                "transaction_count": row["transaction_count"]
            }
            for row in results
        ]

        top_region = results[0]

        return {
            "region": top_region["region"],
            "total_revenue": top_region["total_revenue"] or 0.0,
            "all_regions": all_regions,
            "explanation": f"Region '{top_region['region']}' generated the highest revenue of {top_region['total_revenue']:.2f} from {top_region['transaction_count']} transactions."
        }


def compare_revenue_between_months(month1: int, year1: int, month2: int, year2: int) -> Dict[str, Any]:
    """
    Compare revenue between two specific months.

    Args:
        month1: First month (1-12)
        year1: First year
        month2: Second month (1-12)
        year2: Second year

    Returns:
        Dictionary with month1_revenue, month2_revenue, absolute_change,
        percentage_change, trend, and explanation
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get revenue for first month
        cursor.execute("""
            SELECT SUM(revenue) as total_revenue, COUNT(*) as transaction_count
            FROM sales_transactions
            WHERE revenue IS NOT NULL
            AND strftime('%m', transaction_date) = ?
            AND strftime('%Y', transaction_date) = ?
        """, (f"{month1:02d}", str(year1)))
        result1 = cursor.fetchone()
        month1_revenue = result1["total_revenue"] or 0.0
        month1_count = result1["transaction_count"] or 0

        # Get revenue for second month
        cursor.execute("""
            SELECT SUM(revenue) as total_revenue, COUNT(*) as transaction_count
            FROM sales_transactions
            WHERE revenue IS NOT NULL
            AND strftime('%m', transaction_date) = ?
            AND strftime('%Y', transaction_date) = ?
        """, (f"{month2:02d}", str(year2)))
        result2 = cursor.fetchone()
        month2_revenue = result2["total_revenue"] or 0.0
        month2_count = result2["transaction_count"] or 0

        # Calculate changes
        absolute_change = month2_revenue - month1_revenue

        if month1_revenue != 0:
            percentage_change = (absolute_change / month1_revenue) * 100
        else:
            percentage_change = None

        # Determine trend
        if absolute_change > 0:
            trend = "increased"
        elif absolute_change < 0:
            trend = "decreased"
        else:
            trend = "remained unchanged"

        # Build explanation
        month1_name = datetime(year1, month1, 1).strftime("%B %Y")
        month2_name = datetime(year2, month2, 1).strftime("%B %Y")

        explanation_parts = [
            f"Revenue in {month1_name}: {month1_revenue:.2f} ({month1_count} transactions)",
            f"Revenue in {month2_name}: {month2_revenue:.2f} ({month2_count} transactions)",
            f"Absolute change: {absolute_change:.2f}"
        ]

        if percentage_change is not None:
            explanation_parts.append(f"Percentage change: {percentage_change:.2f}%")

        explanation_parts.append(f"Revenue {trend} from {month1_name} to {month2_name}.")

        return {
            "month1_revenue": month1_revenue,
            "month2_revenue": month2_revenue,
            "absolute_change": absolute_change,
            "percentage_change": percentage_change,
            "trend": trend,
            "explanation": ". ".join(explanation_parts)
        }
