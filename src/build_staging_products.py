
from sqlalchemy import text
from database import get_engine

SQL = """
CREATE TABLE staging.products AS
SELECT
    NULLIF(product_id, '') AS product_id,
    NULLIF(product_category_name, '') AS product_category_name,
    NULLIF(product_name_lenght, '')::integer AS product_name_length,
    NULLIF(product_description_lenght, '')::integer
        AS product_description_length,
    NULLIF(product_photos_qty, '')::integer AS product_photos_qty,
    NULLIF(product_weight_g, '')::numeric(12, 2) AS product_weight_g,
    NULLIF(product_length_cm, '')::numeric(12, 2) AS product_length_cm,
    NULLIF(product_height_cm, '')::numeric(12, 2) AS product_height_cm,
    NULLIF(product_width_cm, '')::numeric(12, 2) AS product_width_cm
FROM raw.products;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS staging.products")
        )
        connection.execute(text(SQL))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM staging.products")
        ).scalar_one()

        missing_ids = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.products
                WHERE product_id IS NULL
            """)
        ).scalar_one()

        missing_weights = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.products
                WHERE product_weight_g IS NULL
            """)
        ).scalar_one()

        print(f"staging.products created: {row_count:,} rows")
        print(f"Rows missing product IDs: {missing_ids:,}")
        print(f"Products with missing weights: {missing_weights:,}")

finally:
    engine.dispose()
