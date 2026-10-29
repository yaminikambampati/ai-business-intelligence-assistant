"""Tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app
from backend.database import init_database, get_db
import sqlite3


@pytest.fixture
def client(temp_db_path, monkeypatch):
    """Create a test client with temporary database."""
    # Monkeypatch database path
    monkeypatch.setattr("backend.database.get_db_path", lambda: temp_db_path)

    # Initialize database with test data
    init_database()

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Insert test data
    test_data = [
        ("TXN001", "2026-01-15", "Laptop Stand", "Accessories", "North", "Online", 10, 1200, 0, "Completed", 12000),
        ("TXN002", "2026-01-20", "Wireless Mouse", "Accessories", "South", "Retail", 25, 650, 0, "Completed", 16250),
        ("TXN003", "2026-02-10", "Monitor", "Electronics", "East", "Online", 6, 9500, 500, "Completed", 56500),
    ]

    for row in test_data:
        cursor.execute("""
            INSERT INTO sales_transactions
            (transaction_id, transaction_date, product, category, region, sales_channel,
             quantity, unit_price, discount_amount, status, revenue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

    conn.commit()
    conn.close()

    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_available"] is True
    assert data["record_count"] > 0


def test_metadata_endpoint(client):
    """Test metadata endpoint."""
    response = client.get("/metadata")
    assert response.status_code == 200

    data = response.json()
    assert data["record_count"] > 0
    assert "date_range" in data
    assert "products" in data
    assert "regions" in data
    assert data["import_status"] == "completed"


def test_ask_total_revenue(client):
    """Test asking for total revenue."""
    response = client.post("/ask", json={"question": "What is the total revenue?"})
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "total_revenue"
    assert "total_revenue" in data["data"]
    assert data["data"]["total_revenue"] == 84750.0  # 12000 + 16250 + 56500


def test_ask_top_product(client):
    """Test asking for top product."""
    response = client.post("/ask", json={"question": "Which product generated the highest revenue?"})
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "top_product"
    assert data["data"]["product"] == "Monitor"


def test_ask_monthly_revenue(client):
    """Test asking for monthly revenue trend."""
    response = client.post("/ask", json={"question": "What is the monthly revenue trend?"})
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "monthly_revenue"
    assert "monthly_data" in data["data"]


def test_ask_top_region(client):
    """Test asking for top region."""
    response = client.post("/ask", json={"question": "Which region generated the highest sales?"})
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["intent"] == "top_region"
    assert "region" in data["data"]


def test_ask_empty_question(client):
    """Test asking with empty question."""
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422  # Pydantic validation error


def test_ask_unsupported_question(client):
    """Test asking an unsupported question."""
    response = client.post("/ask", json={"question": "What is the weather today?"})
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is False
    assert data["intent"] == "unsupported"


def test_analytics_total_revenue_endpoint(client):
    """Test total revenue analytics endpoint."""
    response = client.get("/analytics/total-revenue")
    assert response.status_code == 200

    data = response.json()
    assert data["total_revenue"] == 84750.0
    assert data["transaction_count"] == 3


def test_analytics_top_product_endpoint(client):
    """Test top product analytics endpoint."""
    response = client.get("/analytics/top-product")
    assert response.status_code == 200

    data = response.json()
    assert data["product"] == "Monitor"
    assert data["total_revenue"] == 56500.0


def test_analytics_monthly_revenue_endpoint(client):
    """Test monthly revenue analytics endpoint."""
    response = client.get("/analytics/monthly-revenue")
    assert response.status_code == 200

    data = response.json()
    assert len(data["monthly_data"]) > 0


def test_analytics_top_region_endpoint(client):
    """Test top region analytics endpoint."""
    response = client.get("/analytics/top-region")
    assert response.status_code == 200

    data = response.json()
    assert "region" in data
    assert "total_revenue" in data


def test_analytics_revenue_comparison_endpoint(client):
    """Test revenue comparison analytics endpoint."""
    response = client.get("/analytics/revenue-comparison?month1=1&year1=2026&month2=2&year2=2026")
    assert response.status_code == 200

    data = response.json()
    assert "month1_revenue" in data
    assert "month2_revenue" in data
    assert "absolute_change" in data
