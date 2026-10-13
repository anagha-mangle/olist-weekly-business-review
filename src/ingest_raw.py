
from pathlib import Path
import logging
import sys

import pandas as pd
from sqlalchemy import text

from database import get_engine

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

CHUNK_SIZE = 2_000

EXPECTED_FILES = {
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_customers_dataset.csv": "customers",
    "olist_sellers_dataset.csv": "sellers",
    "olist_products_dataset.csv": "products",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "category_translation",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            LOG_DIR / "raw_ingestion.log", encoding="utf-8"
        ),
    ],
)
logger = logging.getLogger(__name__)


def validate_files():
    missing = [
        filename for filename in EXPECTED_FILES
        if not (RAW_DIR / filename).is_file()
    ]
    if missing:
        raise FileNotFoundError(
            "Missing required CSV files: " + ", ".join(missing)
        )

    for filename, table in EXPECTED_FILES.items():
        columns = pd.read_csv(RAW_DIR / filename, nrows=0).columns.tolist()
        if not columns:
            raise ValueError(f"{filename} has no columns")

        logger.info(
            "Validated %s: %d columns -> raw.%s",
            filename, len(columns), table
        )


def main():
    validate_files()
    engine = get_engine()

    try:
        with engine.begin() as connection:
            # Build replacement tables first. Existing raw tables remain
            # untouched until all nine files have loaded successfully.
            for filename, table in EXPECTED_FILES.items():
                path = RAW_DIR / filename
                load_table = f"_load_{table}"

                logger.info("Starting %s -> raw.%s", filename, load_table)

                # Recreate this run's load table.
                connection.execute(
                    text(f'DROP TABLE IF EXISTS raw."{load_table}"')
                )

                total_rows = 0

                for chunk in pd.read_csv(
                    path,
                    dtype=str,
                    chunksize=CHUNK_SIZE,
                    keep_default_na=False,
                ):
                    chunk.to_sql(
                        load_table,
                        connection,
                        schema="raw",
                        if_exists="append" if total_rows else "replace",
                        index=False,
                        chunksize=CHUNK_SIZE,
                        method="multi",
                    )
                    total_rows += len(chunk)

                    logger.info(
                        "raw.%s: loaded %s rows so far",
                        load_table, f"{total_rows:,}"
                    )

                logger.info(
                    "Finished raw.%s: %s rows",
                    load_table, f"{total_rows:,}"
                )

            # Publish only after every source has loaded successfully.
            for table in EXPECTED_FILES.values():
                connection.execute(
                    text(f'DROP TABLE IF EXISTS raw."{table}" CASCADE')
                )

            for table in EXPECTED_FILES.values():
                connection.execute(
                    text(
                        f'ALTER TABLE raw."_load_{table}" '
                        f'RENAME TO "{table}"'
                    )
                )

            logger.info("All nine raw tables published successfully.")

        with engine.connect() as connection:
            for table in EXPECTED_FILES.values():
                count = connection.execute(
                    text(f'SELECT COUNT(*) FROM raw."{table}"')
                ).scalar_one()
                logger.info(
                    "Verified raw.%s: %s rows", table, f"{count:,}"
                )

        logger.info("Raw ingestion completed successfully.")

    except Exception:
        logger.exception("Raw ingestion FAILED.")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
