"""Tests for data loader."""
import pytest
import pandas as pd
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.data_loader import validate_csv, parse_date, calculate_revenue, DEFAULT_COLUMN_MAPPING


def test_validate_csv_valid_data():
    """Test CSV validation with valid data."""
    df = pd.DataFrame({
        "Transaction_Id": ["TXN001", "TXN002"],
        "Order_date": ["15-01-2026", "20-01-2026"],
        "Product": ["Laptop Stand", "Wireless Mouse"],
        "Region": ["North", "South"],
        "Quantity": [10, 25],
        "Unit_price": [1200, 650]
    })

    valid_count, invalid_count, reasons = validate_csv(df, DEFAULT_COLUMN_MAPPING)

    assert valid_count == 2
    assert invalid_count == 0
    assert len(reasons) == 0


def test_validate_csv_missing_required_field():
    """Test CSV validation with missing required field."""
    df = pd.DataFrame({
        "Transaction_Id": ["TXN001", ""],
        "Order_date": ["15-01-2026", "20-01-2026"],
        "Product": ["Laptop Stand", "Wireless Mouse"],
        "Region": ["North", "South"]
    })

    valid_count, invalid_count, reasons = validate_csv(df, DEFAULT_COLUMN_MAPPING)

    assert valid_count == 1
    assert invalid_count == 1
    assert len(reasons) == 1
    assert "Missing transaction ID" in reasons[0]


def test_validate_csv_negative_quantity():
    """Test CSV validation with negative quantity."""
    df = pd.DataFrame({
        "Transaction_Id": ["TXN001", "TXN002"],
        "Order_date": ["15-01-2026", "20-01-2026"],
        "Product": ["Laptop Stand", "Wireless Mouse"],
        "Region": ["North", "South"],
        "Quantity": [10, -5],
        "Unit_price": [1200, 650]
    })

    valid_count, invalid_count, reasons = validate_csv(df, DEFAULT_COLUMN_MAPPING)

    assert valid_count == 1
    assert invalid_count == 1
    assert "Negative quantity" in reasons[0]


def test_parse_date_valid():
    """Test date parsing with valid format."""
    result = parse_date("15-01-2026", "%d-%m-%Y")
    assert result is not None
    assert result.day == 15
    assert result.month == 1
    assert result.year == 2026


def test_parse_date_invalid():
    """Test date parsing with invalid format."""
    result = parse_date("invalid-date", "%d-%m-%Y")
    assert result is None


def test_calculate_revenue():
    """Test revenue calculation."""
    row = pd.Series({
        "Quantity": 10,
        "Unit_price": 1200,
        "Discount_amount": 500
    })

    revenue = calculate_revenue(row, DEFAULT_COLUMN_MAPPING)
    assert revenue == (10 * 1200) - 500  # 11500


def test_calculate_revenue_with_zero_quantity():
    """Test revenue calculation with zero quantity."""
    row = pd.Series({
        "Quantity": 0,
        "Unit_price": 1200,
        "Discount_amount": 0
    })

    revenue = calculate_revenue(row, DEFAULT_COLUMN_MAPPING)
    assert revenue == 0


def test_calculate_revenue_missing_fields():
    """Test revenue calculation with missing fields."""
    row = pd.Series({
        "Quantity": None,
        "Unit_price": None,
        "Discount_amount": None
    })

    revenue = calculate_revenue(row, DEFAULT_COLUMN_MAPPING)
    assert revenue == 0
