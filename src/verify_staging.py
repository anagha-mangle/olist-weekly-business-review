
from sqlalchemy import text
from database import get_engine

EXPECTED_COUNTS = {
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
failed = []

try:
    with engine.connect() as connection:
        for table, expected in EXPECTED_COUNTS.items():
            actual = connection.execute(
                text(f'SELECT COUNT(*) FROM staging."{table}"')
            ).scalar_one()

            status = "PASS" if actual == expected else "FAIL"

            print(
                f"{status}: staging.{table} | "
                f"expected={expected:,}, actual={actual:,}"
            )

            if actual != expected:
                failed.append(table)

    if failed:
        raise RuntimeError(
            "Staging verification failed for: " + ", ".join(failed)
        )

    print("\nAll nine staging tables verified successfully.")

finally:
    engine.dispose()
