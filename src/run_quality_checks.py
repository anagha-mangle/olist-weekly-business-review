
from sqlalchemy import text
from database import get_engine

# Each query returns the number of failing rows/groups.
# Critical checks stop the pipeline; warnings are reported but don't stop it.
CHECKS = [
    {
        "name": "duplicate_order_ids",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*) FROM (
                SELECT order_id
                FROM staging.orders
                GROUP BY order_id
                HAVING COUNT(*) > 1
            ) AS duplicates
        """,
    },
    {
        "name": "orphan_order_items",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*)
            FROM staging.order_items oi
            LEFT JOIN staging.orders o ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL
        """,
    },
    {
        "name": "orphan_products",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*)
            FROM staging.order_items oi
            LEFT JOIN staging.products p ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL
        """,
    },
    {
        "name": "invalid_review_scores",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*)
            FROM staging.order_reviews
            WHERE review_score IS NULL OR review_score NOT BETWEEN 1 AND 5
        """,
    },
    {
        "name": "duplicate_review_id_groups",
        "severity": "WARNING",
        "sql": """
            SELECT COUNT(*) FROM (
                SELECT review_id
                FROM staging.order_reviews
                WHERE review_id IS NOT NULL
                GROUP BY review_id
                HAVING COUNT(*) > 1
            ) AS duplicates
        """,
    },
    {
        "name": "negative_item_prices",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*) FROM staging.order_items WHERE price < 0
        """,
    },
    {
        "name": "negative_freight_values",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*) FROM staging.order_items WHERE freight_value < 0
        """,
    },
    {
        "name": "missing_purchase_timestamps",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*)
            FROM staging.orders
            WHERE order_purchase_timestamp IS NULL
        """,
    },
    {
        "name": "orphan_sellers",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*)
            FROM staging.order_items oi
            LEFT JOIN staging.sellers s ON oi.seller_id = s.seller_id
            WHERE s.seller_id IS NULL
        """,
    },
    {
        "name": "orphan_payments",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*)
            FROM staging.order_payments p
            LEFT JOIN staging.orders o ON p.order_id = o.order_id
            WHERE o.order_id IS NULL
        """,
    },
    {
        "name": "orphan_customers",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*)
            FROM staging.orders o
            LEFT JOIN staging.customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """,
    },
    {
        "name": "negative_payment_values",
        "severity": "CRITICAL",
        "sql": """
            SELECT COUNT(*)
            FROM staging.order_payments
            WHERE payment_value < 0
        """,
    },
    {
        "name": "invalid_installment_counts",
        "severity": "WARNING",
        "sql": """
            SELECT COUNT(*)
            FROM staging.order_payments
            WHERE payment_installments IS NULL
               OR payment_installments < 1
        """,
    },
]


def main():
    engine = get_engine()
    critical_failures = []
    warning_count = 0

    try:
        with engine.connect() as connection:
            print("\nDATA QUALITY REPORT")
            print("=" * 60)

            for check in CHECKS:
                count = connection.execute(
                    text(check["sql"])
                ).scalar_one()

                if count == 0:
                    status = "PASS"
                elif check["severity"] == "WARNING":
                    status = "WARN"
                    warning_count += 1
                else:
                    status = "FAIL"
                    critical_failures.append(
                        (check["name"], count)
                    )

                print(
                    f"{status:<5} | {check['severity']:<8} | "
                    f"{check['name']:<32} | count={count:,}"
                )

        print("=" * 60)
        print(f"Warnings: {warning_count}")
        print(f"Critical checks failed: {len(critical_failures)}")

        if critical_failures:
            print("\nQUALITY GATE FAILED. Pipeline must stop.")
            for name, count in critical_failures:
                print(f"  - {name}: {count:,} failing rows/groups")
            raise SystemExit(1)

        print("\nQUALITY GATE PASSED.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
