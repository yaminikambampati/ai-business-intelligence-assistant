"""Tests for analytics service."""
import pytest
import sqlite3
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.analytics import (
    get_total_revenue, get_top_product, get_monthly_revenue,
    get_top_region, compare_revenue_between_months
)
from backend.database import get_db


def test_total_revenue(test_db, monkeypatch):
    """Test total revenue calculation."""
    # Monkeypatch the database path
    monkeypatch.setattr("backend.database.get_db_path", lambda: test_db)

    result = get_total_revenue()

    assert result["total_revenue"] == 169650.0  # Sum of all revenues
    assert result["transaction_count"] == 6
    assert "explanation" in result


def test_top_product(test_db, monkeypatch):
    """Test top product calculation."""
    monkeypatch.setattr("backend.database.get_db_path", lambda: test_db)

    result = get_top_product()

    assert result["product"] == "Monitor"  # Highest revenue (56500)
    assert result["total_revenue"] == 56500.0
    assert len(result["all_products"]) == 6  # 6 unique products
    assert "explanation" in result


def test_monthly_revenue(test_db, monkeypatch):
    """Test monthly revenue calculation."""
    monkeypatch.setattr("backend.database.get_db_path", lambda: test_db)

    result = get_monthly_revenue()

    assert len(result["monthly_data"]) == 3  # Jan, Feb, Mar
    assert result["monthly_data"][0]["month"] == "2026-01"
    assert result["date_range"]["start"] == "2026-01-15"
    assert result["date_range"]["end"] == "2026-03-20"
    assert "explanation" in result


def test_top_region(test_db, monkeypatch):
    """Test top region calculation."""
    monkeypatch.setattr("backend.database.get_db_path", lambda: test_db)

    result = get_top_region()

    assert result["region"] in ["North", "South", "East", "West"]
    assert result["total_revenue"] > 0
    assert len(result["all_regions"]) == 4  # 4 unique regions
    assert "explanation" in result


def test_revenue_comparison(test_db, monkeypatch):
    """Test revenue comparison between months."""
    monkeypatch.setattr("backend.database.get_db_path", lambda: test_db)

    result = compare_revenue_between_months(1, 2026, 2, 2026)

    assert "month1_revenue" in result
    assert "month2_revenue" in result
    assert "absolute_change" in result
    assert "trend" in result
    assert "explanation" in result

    # Jan revenue = 12000 + 16250 = 28250
    # Feb revenue = 56500 + 16200 = 72700
    assert result["month1_revenue"] == 28250.0
    assert result["month2_revenue"] == 72700.0
    assert result["absolute_change"] == 44450.0
    assert result["trend"] == "increased"


def test_revenue_comparison_zero_first_month(test_db, monkeypatch):
    """Test revenue comparison when first month has zero revenue."""
    monkeypatch.setattr("backend.database.get_db_path", lambda: test_db)

    result = compare_revenue_between_months(4, 2026, 5, 2026)

    # April has no data
    assert result["month1_revenue"] == 0.0
    assert result["percentage_change"] is None  # Should be None to avoid division by zero
