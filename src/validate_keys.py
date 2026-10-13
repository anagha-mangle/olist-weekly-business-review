
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# Each tuple contains:
# (CSV filename, columns expected to identify one row)
KEYS = [
    ("olist_orders_dataset.csv", ["order_id"]),
    ("olist_order_items_dataset.csv", ["order_id", "order_item_id"]),
    ("olist_order_payments_dataset.csv", ["order_id", "payment_sequential"]),
    ("olist_order_reviews_dataset.csv", ["review_id"]),
    ("olist_customers_dataset.csv", ["customer_id"]),
    ("olist_sellers_dataset.csv", ["seller_id"]),
    ("olist_products_dataset.csv", ["product_id"]),
    (
        "product_category_name_translation.csv",
        ["product_category_name"],
    ),
]

results = []

for filename, key_columns in KEYS:
    path = RAW / filename
    df = pd.read_csv(path, usecols=key_columns, dtype=str)

    null_rows = int(df[key_columns].isna().any(axis=1).sum())
    duplicate_rows = int(
        df.duplicated(subset=key_columns, keep=False).sum()
    )

    result = {
        "table": filename,
        "candidate_key": " + ".join(key_columns),
        "rows": len(df),
        "rows_with_null_key": null_rows,
        "rows_in_duplicate_key_groups": duplicate_rows,
    }
    results.append(result)

    print(f"\n{filename}")
    print(f"  Candidate key: {result['candidate_key']}")
    print(f"  Rows: {len(df):,}")
    print(f"  Rows with null key: {null_rows:,}")
    print(f"  Rows in duplicate key groups: {duplicate_rows:,}")

output = ROOT / "docs" / "key_validation.csv"
pd.DataFrame(results).to_csv(output, index=False)

print(f"\nResults saved to: {output}")
