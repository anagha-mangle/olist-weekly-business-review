
from sqlalchemy import text
from database import get_engine

CREATE_MART = """
CREATE TABLE mart.order_summary AS
WITH item_totals AS (
    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(price) AS product_revenue,
        SUM(freight_value) AS freight_value
    FROM staging.order_items
    GROUP BY order_id
),
payment_totals AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment_value
    FROM staging.order_payments
    GROUP BY order_id
),
review_totals AS (
    SELECT
        order_id,
        AVG(review_score::numeric) AS average_review_score,
        COUNT(*) AS review_count
    FROM staging.order_reviews
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    COALESCE(i.item_count, 0) AS item_count,
    COALESCE(i.product_revenue, 0::numeric) AS product_revenue,
    COALESCE(i.freight_value, 0::numeric) AS freight_value,
    COALESCE(p.total_payment_value, 0::numeric)
        AS total_payment_value,
    r.average_review_score,
    COALESCE(r.review_count, 0) AS review_count,
    CASE
        WHEN o.order_delivered_customer_date IS NOT NULL
         AND o.order_estimated_delivery_date IS NOT NULL
        THEN ROUND(
            (
                EXTRACT(
                    EPOCH FROM (
                        o.order_delivered_customer_date
                        - o.order_estimated_delivery_date
                    )
                ) / 86400.0
            )::numeric,
            2
        )
        ELSE NULL
    END AS delivery_delay_days
FROM staging.orders o
LEFT JOIN staging.customers c
    ON o.customer_id = c.customer_id
LEFT JOIN item_totals i
    ON o.order_id = i.order_id
LEFT JOIN payment_totals p
    ON o.order_id = p.order_id
LEFT JOIN review_totals r
    ON o.order_id = r.order_id;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS mart.order_summary")
        )
        connection.execute(text(CREATE_MART))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM mart.order_summary")
        ).scalar_one()

        distinct_orders = connection.execute(
            text("""
                SELECT COUNT(DISTINCT order_id)
                FROM mart.order_summary
            """)
        ).scalar_one()

        print(f"mart.order_summary rows: {row_count:,}")
        print(f"Distinct orders: {distinct_orders:,}")

        if row_count != distinct_orders:
            raise RuntimeError(
                "Mart grain violation: order_id is not unique."
            )

        print("Mart order-grain verification passed.")

finally:
    engine.dispose()
