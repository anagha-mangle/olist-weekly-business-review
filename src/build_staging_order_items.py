
from sqlalchemy import text
from database import get_engine

SQL = """
CREATE TABLE staging.order_items AS
SELECT
    NULLIF(order_id, '') AS order_id,
    NULLIF(order_item_id, '')::integer AS order_item_id,
    NULLIF(product_id, '') AS product_id,
    NULLIF(seller_id, '') AS seller_id,
    NULLIF(shipping_limit_date, '')::timestamp AS shipping_limit_date,
    NULLIF(price, '')::numeric(12, 2) AS price,
    NULLIF(freight_value, '')::numeric(12, 2) AS freight_value
FROM raw.order_items;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS staging.order_items")
        )
        connection.execute(text(SQL))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM staging.order_items")
        ).scalar_one()

        invalid_numeric_values = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.order_items
                WHERE order_item_id IS NULL
                   OR price IS NULL
                   OR freight_value IS NULL
            """)
        ).scalar_one()

        print(f"staging.order_items created: {row_count:,} rows")
        print(
            "Rows with missing item ID, price, or freight: "
            f"{invalid_numeric_values:,}"
        )

finally:
    engine.dispose()
