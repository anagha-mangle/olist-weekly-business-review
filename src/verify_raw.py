
from sqlalchemy import text
from database import get_engine

EXPECTED = {
    "orders": 99441,
    "order_items": 112650,
    "order_payments": 103886,
    "order_reviews": 99224,
    "customers": 99441,
    "sellers": 3095,
    "products": 32951,
    "geolocation": 1000163,
    "category_translation": 71,
}

engine = get_engine()

try:
    with engine.connect() as connection:
        for table, expected_count in EXPECTED.items():
            actual_count = connection.execute(
                text(f'SELECT COUNT(*) FROM raw."{table}"')
            ).scalar_one()

            status = "PASS" if actual_count == expected_count else "FAIL"
            print(
                f"{status}: raw.{table} | "
                f"expected={expected_count:,}, actual={actual_count:,}"
            )

            if actual_count != expected_count:
                raise RuntimeError(f"Row-count mismatch: raw.{table}")

    print("\nAll nine raw tables verified successfully.")

finally:
    engine.dispose()
