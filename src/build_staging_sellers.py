
from sqlalchemy import text
from database import get_engine

SQL = """
CREATE TABLE staging.sellers AS
SELECT
    NULLIF(seller_id, '') AS seller_id,
    NULLIF(seller_zip_code_prefix, '')::integer
        AS seller_zip_code_prefix,
    NULLIF(seller_city, '') AS seller_city,
    NULLIF(seller_state, '') AS seller_state
FROM raw.sellers;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS staging.sellers")
        )
        connection.execute(text(SQL))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM staging.sellers")
        ).scalar_one()

        missing_ids = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.sellers
                WHERE seller_id IS NULL
            """)
        ).scalar_one()

        missing_states = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.sellers
                WHERE seller_state IS NULL
            """)
        ).scalar_one()

        print(f"staging.sellers created: {row_count:,} rows")
        print(f"Rows missing seller IDs: {missing_ids:,}")
        print(f"Rows missing seller states: {missing_states:,}")

finally:
    engine.dispose()
