
-- 1. Duplicate order IDs: critical failure
SELECT
    'duplicate_order_ids' AS check_name,
    COUNT(*) AS failing_groups
FROM (
    SELECT order_id
    FROM staging.orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
) duplicates;

-- 2. Order items referencing nonexistent orders: critical failure
SELECT
    'orphan_order_items' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.order_items oi
LEFT JOIN staging.orders o
    ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;

-- 3. Order items referencing nonexistent products: critical failure
SELECT
    'orphan_products' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.order_items oi
LEFT JOIN staging.products p
    ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;

-- 4. Invalid review scores: critical failure
SELECT
    'invalid_review_scores' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.order_reviews
WHERE review_score IS NULL
   OR review_score NOT BETWEEN 1 AND 5;

-- 5. Duplicate review IDs: warning to investigate
SELECT
    'duplicate_review_id_groups' AS check_name,
    COUNT(*) AS duplicate_groups
FROM (
    SELECT review_id
    FROM staging.order_reviews
    WHERE review_id IS NOT NULL
    GROUP BY review_id
    HAVING COUNT(*) > 1
) duplicates;

-- 6. Negative order-item prices: critical failure
SELECT
    'negative_item_prices' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.order_items
WHERE price < 0;

-- 7. Negative freight values: critical failure
SELECT
    'negative_freight_values' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.order_items
WHERE freight_value < 0;


-- 8. Missing purchase timestamps: critical failure
SELECT
    'missing_purchase_timestamps' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.orders
WHERE order_purchase_timestamp IS NULL;

-- 9. Order items referencing nonexistent sellers: critical failure
SELECT
    'orphan_sellers' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.order_items oi
LEFT JOIN staging.sellers s
    ON oi.seller_id = s.seller_id
WHERE s.seller_id IS NULL;

-- 10. Payments referencing nonexistent orders: critical failure
SELECT
    'orphan_payments' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.order_payments p
LEFT JOIN staging.orders o
    ON p.order_id = o.order_id
WHERE o.order_id IS NULL;

-- 11. Orders referencing nonexistent customers: critical failure
SELECT
    'orphan_customers' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.orders o
LEFT JOIN staging.customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- 12. Negative payment values: critical failure
SELECT
    'negative_payment_values' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.order_payments
WHERE payment_value < 0;

-- 13. Invalid installment counts: critical failure
SELECT
    'invalid_installment_counts' AS check_name,
    COUNT(*) AS failing_rows
FROM staging.order_payments
WHERE payment_installments IS NULL
   OR payment_installments < 1;
