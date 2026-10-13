
from sqlalchemy import text
from database import get_engine

SQL = """
CREATE TABLE staging.order_reviews AS
SELECT
    NULLIF(review_id, '') AS review_id,
    NULLIF(order_id, '') AS order_id,
    NULLIF(review_score, '')::integer AS review_score,
    NULLIF(review_comment_title, '') AS review_comment_title,
    NULLIF(review_comment_message, '') AS review_comment_message,
    NULLIF(review_creation_date, '')::timestamp
        AS review_creation_date,
    NULLIF(review_answer_timestamp, '')::timestamp
        AS review_answer_timestamp
FROM raw.order_reviews;
"""

engine = get_engine()

try:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS staging.order_reviews")
        )
        connection.execute(text(SQL))

        row_count = connection.execute(
            text("SELECT COUNT(*) FROM staging.order_reviews")
        ).scalar_one()

        invalid_scores = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM staging.order_reviews
                WHERE review_score IS NULL
                   OR review_score NOT BETWEEN 1 AND 5
            """)
        ).scalar_one()

        duplicate_review_ids = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM (
                    SELECT review_id
                    FROM staging.order_reviews
                    WHERE review_id IS NOT NULL
                    GROUP BY review_id
                    HAVING COUNT(*) > 1
                ) AS duplicates
            """)
        ).scalar_one()

        print(f"staging.order_reviews created: {row_count:,} rows")
        print(f"Rows with invalid or missing scores: {invalid_scores:,}")
        print(f"Distinct review IDs appearing more than once: {duplicate_review_ids:,}")

finally:
    engine.dispose()
