"""Pytest configuration and fixtures."""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def test_db(temp_db_path):
    """Create a test database with sample data."""
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE sales_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            transaction_date DATE NOT NULL,
            product TEXT NOT NULL,
            category TEXT,
            region TEXT NOT NULL,
            sales_channel TEXT,
            quantity INTEGER,
            unit_price REAL,
            discount_amount REAL DEFAULT 0,
            status TEXT,
            revenue REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert test data
    test_data = [
        ("TXN001", "2026-01-15", "Laptop Stand", "Accessories", "North", "Online", 10, 1200, 0, "Completed", 12000),
        ("TXN002", "2026-01-20", "Wireless Mouse", "Accessories", "South", "Retail", 25, 650, 0, "Completed", 16250),
        ("TXN003", "2026-02-10", "Monitor", "Electronics", "East", "Online", 6, 9500, 500, "Completed", 56500),
        ("TXN004", "2026-02-15", "Keyboard", "Accessories", "West", "Retail", 18, 900, 0, "Completed", 16200),
        ("TXN005", "2026-03-05", "Office Chair", "Furniture", "North", "Online", 4, 7800, 0, "Completed", 31200),
        ("TXN006", "2026-03-20", "Desk", "Furniture", "South", "Retail", 3, 12500, 0, "Completed", 37500),
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

    return temp_db_path


@pytest.fixture
def sample_csv_data():
    """Create a sample CSV file for testing."""
    import pandas as pd
    from io import StringIO

    csv_content = """Transaction_Id,Order_date,Product,Category,Region,Sales_channel,Quantity,Unit_price,Discount_amount,Status
TXN001,15-01-2026,Laptop Stand,Accessories,North,Online,10,1200,0,Completed
TXN002,20-01-2026,Wireless Mouse,Accessories,South,Retail,25,650,0,Completed
TXN003,10-02-2026,Monitor,Electronics,East,Online,6,9500,500,Completed
TXN004,15-02-2026,Keyboard,Accessories,West,Retail,18,900,0,Completed
TXN005,05-03-2026,Office Chair,Furniture,North,Online,4,7800,0,Completed
"""

    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, 'w') as f:
        f.write(csv_content)

    yield path

    if os.path.exists(path):
        os.unlink(path)
