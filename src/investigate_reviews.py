
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "data" / "raw" / "olist_order_reviews_dataset.csv"

df = pd.read_csv(
    path,
    dtype={"review_id": str, "order_id": str},
)

duplicate_mask = df.duplicated(
    subset=["review_id"], keep=False
)
duplicates = df.loc[duplicate_mask].sort_values("review_id")

print("Total review rows:", len(df))
print("Rows with duplicated review IDs:", len(duplicates))
print("Distinct duplicated review IDs:", duplicates["review_id"].nunique())

# Exclude the grouping key from the comparison.
content_columns = [c for c in df.columns if c != "review_id"]

distinct_versions = (
    duplicates.groupby("review_id")[content_columns]
    .apply(lambda group: len(group.drop_duplicates()))
)

conflicting_ids = distinct_versions[distinct_versions > 1]

print(
    "Review IDs with conflicting order/content records:",
    len(conflicting_ids),
)

print("\nSample conflicting review IDs:")
print(conflicting_ids.head(20).to_string())

# Exact duplicate rows across all columns are a separate check.
exact_duplicate_count = int(df.duplicated(keep=False).sum())
print("\nRows participating in exact full-row duplicates:", exact_duplicate_count)

output = ROOT / "docs" / "duplicate_reviews_sample.csv"
duplicates.head(100).to_csv(output, index=False)

print(f"\nSample saved to: {output}")
