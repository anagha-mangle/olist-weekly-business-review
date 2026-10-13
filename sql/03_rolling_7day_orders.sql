
WITH daily_orders AS (
    SELECT
        order_purchase_timestamp::date AS order_date,
        COUNT(*) AS order_count
    FROM mart.order_summary
    GROUP BY order_purchase_timestamp::date
),
date_calendar AS (
    SELECT GENERATE_SERIES(
        (SELECT MIN(order_date) FROM daily_orders),
        (SELECT MAX(order_date) FROM daily_orders),
        INTERVAL '1 day'
    )::date AS order_date
),
complete_daily_orders AS (
    SELECT
        d.order_date,
        COALESCE(o.order_count, 0) AS order_count
    FROM date_calendar d
    LEFT JOIN daily_orders o
        ON d.order_date = o.order_date
)
SELECT
    order_date,
    order_count,
    ROUND(
        AVG(order_count) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS rolling_7day_avg_orders
FROM complete_daily_orders
ORDER BY order_date;
