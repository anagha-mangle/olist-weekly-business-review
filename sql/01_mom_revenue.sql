
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_purchase_timestamp)::date
            AS order_month,
        SUM(product_revenue) AS monthly_revenue
    FROM mart.order_summary
    WHERE order_status = 'delivered'
    GROUP BY 1
),
month_calendar AS (
    SELECT GENERATE_SERIES(
        (SELECT MIN(order_month) FROM monthly_revenue),
        (SELECT MAX(order_month) FROM monthly_revenue),
        INTERVAL '1 month'
    )::date AS order_month
),
complete_monthly_revenue AS (
    SELECT
        c.order_month,
        COALESCE(m.monthly_revenue, 0) AS monthly_revenue
    FROM month_calendar c
    LEFT JOIN monthly_revenue m
        ON c.order_month = m.order_month
),
revenue_with_previous_month AS (
    SELECT
        order_month,
        monthly_revenue,
        LAG(monthly_revenue) OVER (
            ORDER BY order_month
        ) AS previous_month_revenue
    FROM complete_monthly_revenue
)
SELECT
    order_month,
    ROUND(monthly_revenue::numeric, 2) AS monthly_revenue,
    ROUND(previous_month_revenue::numeric, 2)
        AS previous_month_revenue,
    ROUND(
        100.0 * (
            monthly_revenue - previous_month_revenue
        ) / NULLIF(previous_month_revenue, 0),
        2
    ) AS mom_growth_pct
FROM revenue_with_previous_month
ORDER BY order_month;
