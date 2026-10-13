
WITH delivery_metrics AS (
    SELECT
        CASE
            WHEN delivery_delay_days < 0
                THEN 'Early'
            WHEN delivery_delay_days = 0
                THEN 'On time'
            WHEN delivery_delay_days > 0
                THEN 'Late'
        END AS delivery_status,
        delivery_delay_days,
        average_review_score,
        order_id
    FROM mart.order_summary
    WHERE order_status = 'delivered'
      AND delivery_delay_days IS NOT NULL
)
SELECT
    delivery_status,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(AVG(delivery_delay_days)::numeric, 2)
        AS average_delay_days,
    ROUND(AVG(average_review_score)::numeric, 2)
        AS average_review_score,
    COUNT(*) FILTER (
        WHERE average_review_score IS NOT NULL
    ) AS orders_with_reviews
FROM delivery_metrics
GROUP BY delivery_status
ORDER BY
    CASE delivery_status
        WHEN 'Early' THEN 1
        WHEN 'On time' THEN 2
        WHEN 'Late' THEN 3
    END;
