
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DOCS_DIR = ROOT / "docs"

EXPECTED_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
]

inventory = []
missing = []

for filename in EXPECTED_FILES:
    path = RAW_DIR / filename

    if not path.exists():
        missing.append(filename)
        print(f"MISSING: {filename}")
        continue

    columns = pd.read_csv(path, nrows=0).columns.tolist()

    # Count CSV records using the CSV parser, including proper
    # handling of quoted fields.
    row_count = sum(
        len(chunk)
        for chunk in pd.read_csv(path, chunksize=100_000)
    )

    inventory.append({
        "file": filename,
        "row_count": row_count,
        "column_count": len(columns),
        "columns": ", ".join(columns),
    })

    print(f"{filename}: {row_count:,} rows, {len(columns)} columns")

if missing:
    raise FileNotFoundError(
        "Missing required CSV files: " + ", ".join(missing)
    )

DOCS_DIR.mkdir(parents=True, exist_ok=True)

output = DOCS_DIR / "dataset_inventory.csv"
pd.DataFrame(inventory).to_csv(output, index=False)

print(f"\nInventory saved to: {output}")
print("All expected CSV files were found.")
