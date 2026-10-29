"""Tests for SQL security and query validation."""
import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.query_validator import SQLValidator


def test_valid_select_query():
    """Test that valid SELECT queries are allowed."""
    query = "SELECT * FROM sales_transactions"
    is_valid, message = SQLValidator.validate_query(query)
    assert is_valid is True
    assert message == "Query is valid"


def test_delete_query_rejected():
    """Test that DELETE queries are rejected."""
    query = "DELETE FROM sales_transactions"
    is_valid, message = SQLValidator.validate_query(query)
    assert is_valid is False
    assert "Forbidden keyword" in message


def test_drop_query_rejected():
    """Test that DROP queries are rejected."""
    query = "DROP TABLE sales_transactions"
    is_valid, message = SQLValidator.validate_query(query)
    assert is_valid is False
    assert "Forbidden keyword" in message


def test_update_query_rejected():
    """Test that UPDATE queries are rejected."""
    query = "UPDATE sales_transactions SET revenue = 0"
    is_valid, message = SQLValidator.validate_query(query)
    assert is_valid is False
    assert "Forbidden keyword" in message


def test_insert_query_rejected():
    """Test that INSERT queries are rejected."""
    query = "INSERT INTO sales_transactions VALUES (...)"
    is_valid, message = SQLValidator.validate_query(query)
    assert is_valid is False
    assert "Forbidden keyword" in message


def test_multiple_statements_rejected():
    """Test that multiple statements are rejected."""
    query = "SELECT * FROM sales_transactions; DROP TABLE users"
    is_valid, message = SQLValidator.validate_query(query)
    assert is_valid is False
    # Either multiple statements or forbidden keyword detection is acceptable
    assert "Multiple statements" in message or "Forbidden keyword" in message


def test_sql_comment_rejected():
    """Test that SQL comments are rejected."""
    query = "SELECT * FROM sales_transactions -- comment"
    is_valid, message = SQLValidator.validate_query(query)
    assert is_valid is False
    assert "SQL comments" in message


def test_unauthorized_table_rejected():
    """Test that queries on unauthorized tables are rejected."""
    query = "SELECT * FROM sqlite_master"
    is_valid, message = SQLValidator.validate_query(query)
    assert is_valid is False
    assert "allowed tables" in message.lower()


def test_destructive_queries_test():
    """Test the destructive queries test suite."""
    results = SQLValidator.test_destructive_queries()

    # All test queries should pass validation (i.e., be correctly identified as valid/invalid)
    for query, passed in results:
        assert passed is True, f"Query failed test: {query}"
