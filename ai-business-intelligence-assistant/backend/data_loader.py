"""CSV data loader with validation and database ingestion."""
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging

from backend.database import init_database, get_db
from backend.schemas import ColumnMapping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Default column mapping for the supplied CSV
DEFAULT_COLUMN_MAPPING = ColumnMapping(
    transaction_id="Transaction_Id",
    transaction_date="Order_date",
    product="Product",
    category="Category",
    region="Region",
    sales_channel="Sales_channel",
    quantity="Quantity",
    unit_price="Unit_price",
    discount_amount="Discount_amount",
    status="Status"
)


def validate_csv(df: pd.DataFrame, mapping: ColumnMapping) -> Tuple[int, int, list]:
    """
    Validate the CSV dataframe and return valid/invalid counts with reasons.

    Returns:
        Tuple of (valid_count, invalid_count, rejection_reasons)
    """
    required_columns = [
        mapping.transaction_id,
        mapping.transaction_date,
        mapping.product,
        mapping.region
    ]

    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    valid_count = 0
    invalid_count = 0
    rejection_reasons = []

    for idx, row in df.iterrows():
        is_valid = True
        reasons = []

        # Check for missing required fields
        if pd.isna(row[mapping.transaction_id]) or str(row[mapping.transaction_id]).strip() == "":
            is_valid = False
            reasons.append("Missing transaction ID")

        if pd.isna(row[mapping.transaction_date]) or str(row[mapping.transaction_date]).strip() == "":
            is_valid = False
            reasons.append("Missing transaction date")

        if pd.isna(row[mapping.product]) or str(row[mapping.product]).strip() == "":
            is_valid = False
            reasons.append("Missing product")

        if pd.isna(row[mapping.region]) or str(row[mapping.region]).strip() == "":
            is_valid = False
            reasons.append("Missing region")

        # Check for invalid quantity (negative values)
        if mapping.quantity and mapping.quantity in df.columns:
            qty = row[mapping.quantity]
            if pd.notna(qty):
                try:
                    qty_val = float(qty)
                    if qty_val < 0:
                        is_valid = False
                        reasons.append("Negative quantity")
                except (ValueError, TypeError):
                    reasons.append("Invalid quantity format")

        # Check for invalid unit price (negative values)
        if mapping.unit_price and mapping.unit_price in df.columns:
            price = row[mapping.unit_price]
            if pd.notna(price):
                try:
                    price_val = float(price)
                    if price_val < 0:
                        is_valid = False
                        reasons.append("Negative unit price")
                except (ValueError, TypeError):
                    reasons.append("Invalid unit price format")

        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            rejection_reasons.append(f"Row {idx + 2}: {', '.join(reasons)}")

    return valid_count, invalid_count, rejection_reasons


def parse_date(date_str: str, date_format: str = "%d-%m-%Y") -> Optional[datetime]:
    """Parse date string with error handling."""
    try:
        return datetime.strptime(str(date_str).strip(), date_format)
    except (ValueError, TypeError):
        return None


def calculate_revenue(row: pd.Series, mapping: ColumnMapping) -> Optional[float]:
    """
    Calculate revenue from quantity, unit price, and discount.

    Revenue = (Quantity × Unit_price) - Discount_amount
    """
    try:
        quantity = 0
        unit_price = 0
        discount = 0

        if mapping.quantity and mapping.quantity in row.index:
            qty_val = row[mapping.quantity]
            if pd.notna(qty_val):
                quantity = float(qty_val)

        if mapping.unit_price and mapping.unit_price in row.index:
            price_val = row[mapping.unit_price]
            if pd.notna(price_val):
                unit_price = float(price_val)

        if mapping.discount_amount and mapping.discount_amount in row.index:
            discount_val = row[mapping.discount_amount]
            if pd.notna(discount_val):
                discount = float(discount_val)

        revenue = (quantity * unit_price) - discount
        return revenue
    except (ValueError, TypeError):
        return None


def normalize_column_name(col: str) -> str:
    """Normalize column name by lowercasing and replacing spaces with underscores."""
    return col.strip().lower().replace(" ", "_").replace("-", "_")


def load_csv_to_database(
    csv_path: str,
    mapping: Optional[ColumnMapping] = None,
    date_format: str = "%d-%m-%Y"
) -> Dict[str, any]:
    """
    Load CSV data into SQLite database.

    Args:
        csv_path: Path to the CSV file
        mapping: Column mapping configuration
        date_format: Date format for parsing

    Returns:
        Dictionary with import statistics
    """
    if mapping is None:
        mapping = DEFAULT_COLUMN_MAPPING

    # Read CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {e}")

    logger.info(f"Loaded {len(df)} rows from CSV")

    # Validate CSV
    valid_count, invalid_count, rejection_reasons = validate_csv(df, mapping)
    logger.info(f"Validation: {valid_count} valid, {invalid_count} invalid")

    # Initialize database
    init_database()

    # Load data into database
    loaded_count = 0
    skipped_count = 0
    skipped_reasons = []

    with get_db() as conn:
        cursor = conn.cursor()

        for idx, row in df.iterrows():
            # Skip invalid rows
            if pd.isna(row[mapping.transaction_id]) or str(row[mapping.transaction_id]).strip() == "":
                skipped_count += 1
                skipped_reasons.append(f"Row {idx + 2}: Missing transaction ID")
                continue

            if pd.isna(row[mapping.transaction_date]) or str(row[mapping.transaction_date]).strip() == "":
                skipped_count += 1
                skipped_reasons.append(f"Row {idx + 2}: Missing transaction date")
                continue

            # Parse date
            parsed_date = parse_date(row[mapping.transaction_date], date_format)
            if parsed_date is None:
                skipped_count += 1
                skipped_reasons.append(f"Row {idx + 2}: Invalid date format")
                continue

            # Calculate revenue
            revenue = calculate_revenue(row, mapping)

            # Extract fields
            transaction_id = str(row[mapping.transaction_id]).strip()
            product = str(row[mapping.product]).strip()
            region = str(row[mapping.region]).strip()

            category = None
            if mapping.category and mapping.category in row.index and pd.notna(row[mapping.category]):
                category = str(row[mapping.category]).strip()

            sales_channel = None
            if mapping.sales_channel and mapping.sales_channel in row.index and pd.notna(row[mapping.sales_channel]):
                sales_channel = str(row[mapping.sales_channel]).strip()

            quantity = None
            if mapping.quantity and mapping.quantity in row.index and pd.notna(row[mapping.quantity]):
                try:
                    quantity = int(float(row[mapping.quantity]))
                except (ValueError, TypeError):
                    pass

            unit_price = None
            if mapping.unit_price and mapping.unit_price in row.index and pd.notna(row[mapping.unit_price]):
                try:
                    unit_price = float(row[mapping.unit_price])
                except (ValueError, TypeError):
                    pass

            discount_amount = 0
            if mapping.discount_amount and mapping.discount_amount in row.index and pd.notna(row[mapping.discount_amount]):
                try:
                    discount_amount = float(row[mapping.discount_amount])
                except (ValueError, TypeError):
                    pass

            status = None
            if mapping.status and mapping.status in row.index and pd.notna(row[mapping.status]):
                status = str(row[mapping.status]).strip()

            # Insert into database (skip duplicates)
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO sales_transactions
                    (transaction_id, transaction_date, product, category, region, sales_channel,
                     quantity, unit_price, discount_amount, status, revenue)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction_id,
                    parsed_date.strftime("%Y-%m-%d"),
                    product,
                    category,
                    region,
                    sales_channel,
                    quantity,
                    unit_price,
                    discount_amount,
                    status,
                    revenue
                ))
                if cursor.rowcount > 0:
                    loaded_count += 1
                else:
                    skipped_count += 1
                    skipped_reasons.append(f"Row {idx + 2}: Duplicate transaction ID")
            except Exception as e:
                skipped_count += 1
                skipped_reasons.append(f"Row {idx + 2}: Database error - {str(e)}")

    return {
        "total_rows": len(df),
        "valid_rows": valid_count,
        "invalid_rows": invalid_count,
        "loaded_rows": loaded_count,
        "skipped_rows": skipped_count,
        "rejection_reasons": rejection_reasons[:10],  # First 10 reasons
        "skipped_reasons": skipped_reasons[:10]  # First 10 reasons
    }


def main():
    """Command-line interface for data loading."""
    parser = argparse.ArgumentParser(description="Load sales CSV data into SQLite database")
    parser.add_argument("--csv", required=True, help="Path to the CSV file")
    parser.add_argument("--date-format", default="%d-%m-%Y", help="Date format (default: %%d-%%m-%%Y)")

    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return

    logger.info(f"Loading CSV from: {csv_path}")

    try:
        result = load_csv_to_database(str(csv_path), date_format=args.date_format)

        print("\n" + "="*60)
        print("CSV IMPORT SUMMARY")
        print("="*60)
        print(f"Total rows in CSV: {result['total_rows']}")
        print(f"Valid rows: {result['valid_rows']}")
        print(f"Invalid rows: {result['invalid_rows']}")
        print(f"Loaded into database: {result['loaded_rows']}")
        print(f"Skipped (duplicates/errors): {result['skipped_rows']}")
        print("="*60)

        if result['rejection_reasons']:
            print("\nRejection reasons (first 10):")
            for reason in result['rejection_reasons']:
                print(f"  - {reason}")

        if result['skipped_reasons']:
            print("\nSkip reasons (first 10):")
            for reason in result['skipped_reasons']:
                print(f"  - {reason}")

        print("\nImport completed successfully!")

    except Exception as e:
        logger.error(f"Failed to load CSV: {e}")
        raise


if __name__ == "__main__":
    main()
