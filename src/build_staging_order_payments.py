
from sqlalchemy import text
from database import get_engine

SQL = """
CREATE TABLE staging.order_payments AS
SELECT
    NULLIF(order_id, '') AS order_id,
    NULLIF(payment_sequential, '')::integer AS payment_sequential,
    NULLIF(payment_type, '') AS payment_type,
    NULLIF(payment_installments, '')::integer AS payment_installments,
    NULLIF(payment_value, '')::numeric(12, 2) AS payment_value
FROM raw.order_payments;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS staging.order_payments")
        )
        connection.execute(text(SQL))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM staging.order_payments")
        ).scalar_one()

        invalid_values = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.order_payments
                WHERE order_id IS NULL
                   OR payment_sequential IS NULL
                   OR payment_installments IS NULL
                   OR payment_value IS NULL
            """)
        ).scalar_one()

        print(f"staging.order_payments created: {row_count:,} rows")
        print(f"Rows with missing required values: {invalid_values:,}")

finally:
    engine.dispose()
