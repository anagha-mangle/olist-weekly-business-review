
from sqlalchemy import text
from database import get_engine

SQL = """
CREATE TABLE staging.orders AS
SELECT
    NULLIF(order_id, '') AS order_id,
    NULLIF(customer_id, '') AS customer_id,
    NULLIF(order_status, '') AS order_status,
    NULLIF(order_purchase_timestamp, '')::timestamp
        AS order_purchase_timestamp,
    NULLIF(order_approved_at, '')::timestamp
        AS order_approved_at,
    NULLIF(order_delivered_carrier_date, '')::timestamp
        AS order_delivered_carrier_date,
    NULLIF(order_delivered_customer_date, '')::timestamp
        AS order_delivered_customer_date,
    NULLIF(order_estimated_delivery_date, '')::timestamp
        AS order_estimated_delivery_date
FROM raw.orders;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS staging.orders"))
        connection.execute(text(SQL))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM staging.orders")
        ).scalar_one()

        null_purchase_dates = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.orders
                WHERE order_purchase_timestamp IS NULL
            """)
        ).scalar_one()

        print(f"staging.orders created: {row_count:,} rows")
        print(
            "Rows with missing purchase timestamps: "
            f"{null_purchase_dates:,}"
        )

finally:
    engine.dispose()
