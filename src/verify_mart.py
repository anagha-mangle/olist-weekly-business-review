
from sqlalchemy import text
from database import get_engine

SQL = """
SELECT
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE product_revenue > 0
    ) AS orders_with_revenue,
    ROUND(SUM(product_revenue), 2) AS total_product_revenue,
    ROUND(SUM(freight_value), 2) AS total_freight,
    ROUND(SUM(total_payment_value), 2) AS total_payments,
    COUNT(*) FILTER (
        WHERE delivery_delay_days IS NOT NULL
    ) AS orders_with_delivery_delay,
    ROUND(AVG(delivery_delay_days), 2) AS average_delivery_delay_days,
    COUNT(*) FILTER (
        WHERE delivery_delay_days > 0
    ) AS orders_delivered_late,
    COUNT(*) FILTER (
        WHERE average_review_score IS NOT NULL
    ) AS orders_with_reviews
FROM mart.order_summary;
"""

engine = get_engine()

try:
    with engine.connect() as connection:
        result = connection.execute(text(SQL)).mappings().one()

        print("MART BUSINESS SUMMARY")
        print("=" * 45)
        for metric, value in result.items():
            print(f"{metric}: {value}")

finally:
    engine.dispose()
