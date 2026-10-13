
from sqlalchemy import text
from database import get_engine

SQL = """
CREATE TABLE staging.category_translation AS
SELECT
    NULLIF(product_category_name, '') AS product_category_name,
    NULLIF(product_category_name_english, '') AS product_category_name_english
FROM raw.category_translation;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS staging.category_translation")
        )
        connection.execute(text(SQL))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM staging.category_translation")
        ).scalar_one()

        missing_values = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.category_translation
                WHERE product_category_name IS NULL
                   OR product_category_name_english IS NULL
            """)
        ).scalar_one()

        duplicate_categories = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM (
                    SELECT product_category_name
                    FROM staging.category_translation
                    WHERE product_category_name IS NOT NULL
                    GROUP BY product_category_name
                    HAVING COUNT(*) > 1
                ) AS duplicates
            """)
        ).scalar_one()

        print(
            f"staging.category_translation created: {row_count:,} rows"
        )
        print(f"Rows with missing category names: {missing_values:,}")
        print(f"Duplicated source category names: {duplicate_categories:,}")

finally:
    engine.dispose()
