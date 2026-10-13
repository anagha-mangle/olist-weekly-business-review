
from sqlalchemy import text
from database import get_engine

SQL = """
CREATE TABLE staging.geolocation AS
SELECT
    NULLIF(geolocation_zip_code_prefix, '')::integer
        AS geolocation_zip_code_prefix,
    NULLIF(geolocation_lat, '')::numeric(12, 8) AS geolocation_lat,
    NULLIF(geolocation_lng, '')::numeric(12, 8) AS geolocation_lng,
    NULLIF(geolocation_city, '') AS geolocation_city,
    NULLIF(geolocation_state, '') AS geolocation_state
FROM raw.geolocation;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS staging.geolocation")
        )
        connection.execute(text(SQL))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM staging.geolocation")
        ).scalar_one()

        missing_coordinates = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.geolocation
                WHERE geolocation_lat IS NULL
                   OR geolocation_lng IS NULL
            """)
        ).scalar_one()

        invalid_coordinates = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.geolocation
                WHERE geolocation_lat NOT BETWEEN -90 AND 90
                   OR geolocation_lng NOT BETWEEN -180 AND 180
            """)
        ).scalar_one()

        print(f"staging.geolocation created: {row_count:,} rows")
        print(f"Rows missing coordinates: {missing_coordinates:,}")
        print(f"Rows with out-of-range coordinates: {invalid_coordinates:,}")

finally:
    engine.dispose()
