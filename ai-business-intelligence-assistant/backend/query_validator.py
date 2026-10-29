"""Query validation for SQL security."""
import re
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class SQLValidator:
    """Validator for SQL queries to prevent injection and unauthorized operations."""

    # Forbidden SQL keywords
    FORBIDDEN_KEYWORDS = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
        "REPLACE", "ATTACH", "DETACH", "PRAGMA", "GRANT", "REVOKE",
        "TRUNCATE", "EXEC", "EXECUTE", "MERGE", "CALL"
    ]

    # Allowed tables
    ALLOWED_TABLES = ["sales_transactions"]

    # Allowed patterns for SELECT
    ALLOWED_PATTERNS = [
        r"^SELECT\s+.+\s+FROM\s+sales_transactions",
        r"^SELECT\s+.+\s+FROM\s+\(\s*SELECT"
    ]

    @classmethod
    def validate_query(cls, query: str) -> Tuple[bool, str]:
        """
        Validate a SQL query for safety.

        Args:
            query: The SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        query_upper = query.upper().strip()

        # Check for forbidden keywords
        for keyword in cls.FORBIDDEN_KEYWORDS:
            if keyword in query_upper:
                return False, f"Forbidden keyword '{keyword}' detected"

        # Check for multiple statements (semicolon separator)
        if ";" in query[:-1]:  # Allow trailing semicolon
            return False, "Multiple statements not allowed"

        # Check for comment-based injection attempts
        if "--" in query or "/*" in query:
            return False, "SQL comments not allowed"

        # Check that it starts with SELECT
        if not query_upper.startswith("SELECT"):
            return False, "Only SELECT queries are allowed"

        # Check for allowed tables
        table_found = False
        for table in cls.ALLOWED_TABLES:
            if table.upper() in query_upper:
                table_found = True
                break

        if not table_found:
            return False, f"Query must use one of the allowed tables: {cls.ALLOWED_TABLES}"

        # Check for suspicious patterns
        suspicious_patterns = [
            r"\bEXEC\b",
            r"\bEXECUTE\b",
            r"\bSCRIPT\b",
            r"\bSHUTDOWN\b",
            r"\bVACUUM\b"
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return False, f"Suspicious pattern detected: {pattern}"

        return True, "Query is valid"

    @classmethod
    def test_destructive_queries(cls) -> List[Tuple[str, bool]]:
        """
        Test that destructive queries are rejected.

        Returns:
            List of (query, should_be_rejected) tuples
        """
        test_queries = [
            ("SELECT * FROM sales_transactions", True),  # Should be allowed
            ("DELETE FROM sales_transactions", False),  # Should be rejected
            ("DROP TABLE sales_transactions", False),  # Should be rejected
            ("UPDATE sales_transactions SET revenue = 0", False),  # Should be rejected
            ("INSERT INTO sales_transactions VALUES (...)", False),  # Should be rejected
            ("SELECT * FROM sales_transactions; DROP TABLE users", False),  # Should be rejected
            ("SELECT * FROM sales_transactions -- comment", False),  # Should be rejected
            ("SELECT * FROM sqlite_master", False),  # Should be rejected
        ]

        results = []
        for query, should_be_valid in test_queries:
            is_valid, _ = cls.validate_query(query)
            results.append((query, is_valid == should_be_valid))

        return results
