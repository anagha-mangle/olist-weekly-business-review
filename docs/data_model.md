\# Olist Data Model



\## 1. Dataset overview



The Olist Brazilian E-Commerce dataset contains nine CSV files representing orders, items, payments, reviews, customers, sellers, products, geolocation and category translations.



The raw layer preserves source records. The staging layer standardizes types and validates relationships. The mart layer provides an order-level dataset for business analysis.



\## 2. Source tables and grain



| Table | Grain | Primary or candidate key |

|---|---|---|

| orders | One row per order | order\_id |

| order\_items | One row per item within an order | order\_id, order\_item\_id |

| order\_payments | One row per payment sequence within an order | order\_id, payment\_sequential |

| order\_reviews | One row per review record | review\_id (validate uniqueness) |

| customers | One row per order-linked customer record | customer\_id |

| sellers | One row per seller | seller\_id |

| products | One row per product | product\_id |

| geolocation | One row per geographic source record | No assumed unique key |

| category\_translation | One row per category mapping | product\_category\_name (validate uniqueness) |



\## 3. Foreign-key relationships



\- orders.customer\_id references customers.customer\_id.

\- order\_items.order\_id references orders.order\_id.

\- order\_items.product\_id references products.product\_id.

\- order\_items.seller\_id references sellers.seller\_id.

\- order\_payments.order\_id references orders.order\_id.

\- order\_reviews.order\_id references orders.order\_id.



Customer and seller ZIP-code prefixes can be related to geolocation through their corresponding ZIP-prefix columns. However, geolocation may contain multiple records per prefix, so it must be deduplicated or aggregated before joining.



Products can be associated with English category names using product\_category\_name and the category translation table.



\## 4. Important analytical considerations



1\. customer\_id identifies the customer record linked to an order; customer\_unique\_id is used to identify a customer across multiple orders.

2\. Orders, order items, payments and reviews have different grains.

3\. Item and payment totals must be aggregated separately before joining them to orders.

4\. The reviews table may contain multiple records associated with an order. Review aggregation rules must be documented.

5\. Missing timestamps should remain missing rather than being replaced with fabricated dates.

6\. Revenue calculations must explicitly define included order statuses and whether freight is included.

7\. All candidate keys and foreign-key relationships must be validated before relying on them in analytical queries.



\## 5. Target mart



The target mart.order\_summary table contains one row per order, with customer identity and state, order status, purchase and delivery timestamps, aggregated item and freight totals, aggregated payment value, review score and delivery delay.



The order\_id column is the primary key of this mart. The mart is rebuilt from staging data only after the required transformations and data-quality checks succeed.

