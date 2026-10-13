
WITH category_revenue AS (
    SELECT
        c.customer_state,
        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'unknown'
        ) AS product_category,
        SUM(oi.price) AS product_revenue
    FROM staging.orders o
    JOIN staging.customers c
        ON o.customer_id = c.customer_id
    JOIN staging.order_items oi
        ON o.order_id = oi.order_id
    JOIN staging.products p
        ON oi.product_id = p.product_id
    LEFT JOIN staging.category_translation t
        ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY
        c.customer_state,
        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'unknown'
        )
),
ranked_categories AS (
    SELECT
        customer_state,
        product_category,
        product_revenue,
        DENSE_RANK() OVER (
            PARTITION BY customer_state
            ORDER BY product_revenue DESC
        ) AS category_rank
    FROM category_revenue
)
SELECT
    customer_state,
    category_rank,
    product_category,
    ROUND(product_revenue::numeric, 2) AS product_revenue
FROM ranked_categories
WHERE category_rank <= 3
ORDER BY
    customer_state,
    category_rank,
    product_category;
