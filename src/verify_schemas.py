
from sqlalchemy import text
from database import get_engine

engine = get_engine()

try:
    with engine.connect() as connection:
        rows = connection.execute(text("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name IN ('raw', 'staging', 'mart')
            ORDER BY schema_name;
        """)).scalars().all()

    print("Schemas found:", rows)

    expected = {"raw", "staging", "mart"}
    if set(rows) != expected:
        raise RuntimeError(
            f"Schema mismatch. Expected {expected}, found {set(rows)}"
        )

    print("All three project schemas verified successfully.")

finally:
    engine.dispose()
