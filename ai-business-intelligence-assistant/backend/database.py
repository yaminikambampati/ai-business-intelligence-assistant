"""Database connection and session management."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional
from backend.config import settings


def get_db_path() -> str:
    """Get the absolute path to the database file."""
    db_path = Path(settings.database_path)
    if not db_path.is_absolute():
        db_path = Path(__file__).parent.parent / db_path
    return str(db_path)


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db() -> sqlite3.Connection:
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database() -> None:
    """Initialize the database schema."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_transactions (
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
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transaction_date 
            ON sales_transactions(transaction_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_product 
            ON sales_transactions(product)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_region 
            ON sales_transactions(region)
        """)


def is_database_available() -> bool:
    """Check if the database is available and has data."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sales_transactions")
            count = cursor.fetchone()[0]
            return count > 0
    except Exception:
        return False


def get_record_count() -> int:
    """Get the total number of records in the database."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sales_transactions")
            return cursor.fetchone()[0]
    except Exception:
        return 0
