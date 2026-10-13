
from sqlalchemy import text
from database import get_engine

SQL = """
CREATE TABLE staging.customers AS
SELECT
    NULLIF(customer_id, '') AS customer_id,
    NULLIF(customer_unique_id, '') AS customer_unique_id,
    NULLIF(customer_zip_code_prefix, '')::integer
        AS customer_zip_code_prefix,
    NULLIF(customer_city, '') AS customer_city,
    NULLIF(customer_state, '') AS customer_state
FROM raw.customers;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS staging.customers")
        )
        connection.execute(text(SQL))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM staging.customers")
        ).scalar_one()

        missing_values = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.customers
                WHERE customer_id IS NULL
                   OR customer_unique_id IS NULL
                   OR customer_state IS NULL
            """)
        ).scalar_one()

        unique_customers = connection.execute(
            text("""
                SELECT COUNT(DISTINCT customer_unique_id)
                FROM staging.customers
            """)
        ).scalar_one()

        print(f"staging.customers created: {row_count:,} rows")
        print(f"Rows missing required values: {missing_values:,}")
        print(f"Distinct customer identities: {unique_customers:,}")

finally:
    engine.dispose()
