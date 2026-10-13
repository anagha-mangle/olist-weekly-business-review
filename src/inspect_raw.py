
from sqlalchemy import text
from database import get_engine

engine = get_engine()

try:
    with engine.connect() as connection:
        rows = connection.execute(
            text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'staging'
                  AND table_name = 'orders'
                ORDER BY ordinal_position;
            """)
        ).fetchall()

        for column_name, data_type in rows:
            print(f"{column_name}: {data_type}")

finally:
    engine.dispose()
