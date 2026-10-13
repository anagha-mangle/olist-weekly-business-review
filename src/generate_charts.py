
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sqlalchemy import text

from database import get_engine


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHART_DIR = PROJECT_ROOT / "reports" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)


QUERIES = {
    "monthly_revenue": """
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
        )
        SELECT
            c.order_month,
            COALESCE(m.monthly_revenue, 0) AS monthly_revenue
        FROM month_calendar c
        LEFT JOIN monthly_revenue m
            ON c.order_month = m.order_month
        ORDER BY c.order_month;
    """,

    "top_categories": """
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
                ON p.product_category_name =
                   t.product_category_name
            WHERE o.order_status = 'delivered'
            GROUP BY 1, 2
        ),
        ranked AS (
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
            product_revenue
        FROM ranked
        WHERE category_rank <= 3
        ORDER BY customer_state, category_rank, product_category;
    """,

    "rolling_orders": """
        WITH daily_orders AS (
            SELECT
                order_purchase_timestamp::date AS order_date,
                COUNT(*) AS order_count
            FROM mart.order_summary
            GROUP BY 1
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
            AVG(order_count) OVER (
                ORDER BY order_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) AS rolling_7day_avg_orders
        FROM complete_daily_orders
        ORDER BY order_date;
    """,

    "delivery_reviews": """
        SELECT
            CASE
                WHEN delivery_delay_days < 0 THEN 'Early'
                WHEN delivery_delay_days = 0 THEN 'On time'
                WHEN delivery_delay_days > 0 THEN 'Late'
            END AS delivery_status,
            COUNT(*) AS order_count,
            AVG(delivery_delay_days) AS average_delay_days,
            AVG(average_review_score) AS average_review_score
        FROM mart.order_summary
        WHERE order_status = 'delivered'
          AND delivery_delay_days IS NOT NULL
        GROUP BY 1
        ORDER BY CASE
            WHEN
                CASE
                    WHEN delivery_delay_days < 0 THEN 'Early'
                    WHEN delivery_delay_days = 0 THEN 'On time'
                    WHEN delivery_delay_days > 0 THEN 'Late'
                END = 'Early' THEN 1
            WHEN
                CASE
                    WHEN delivery_delay_days < 0 THEN 'Early'
                    WHEN delivery_delay_days = 0 THEN 'On time'
                    WHEN delivery_delay_days > 0 THEN 'Late'
                END = 'On time' THEN 2
            ELSE 3
        END;
    """,
}


def fetch_rows(connection, query):
    return connection.execute(text(query)).mappings().all()


def save_chart(fig, filename):
    output_path = CHART_DIR / filename
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved: {output_path}")


def chart_monthly_revenue(rows):
    months = [row["order_month"] for row in rows]
    revenue = [float(row["monthly_revenue"] or 0) for row in rows]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(months, revenue, marker="o", linewidth=2, markersize=4)
    ax.set_title("Monthly Delivered Product Revenue")
    ax.set_xlabel("Order month")
    ax.set_ylabel("Product revenue (BRL)")
    ax.grid(axis="y", alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()

    save_chart(fig, "01_monthly_revenue.png")
    print(f"Months plotted: {len(rows)}")
    print(f"Total product revenue: R${sum(revenue):,.2f}")


def chart_top_categories(rows):
    # Show the top category in each of the ten highest-revenue states.
    state_totals = {}
    for row in rows:
        state_totals[row["customer_state"]] = (
            state_totals.get(row["customer_state"], 0)
            + float(row["product_revenue"])
        )

    top_states = {
        state for state, _ in sorted(
            state_totals.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:10]
    }

    top_rows = [
        row for row in rows
        if row["customer_state"] in top_states
        and row["category_rank"] == 1
    ]
    top_rows.sort(key=lambda row: float(row["product_revenue"]))

    labels = [
        f'{row["customer_state"]} — {row["product_category"]}'
        for row in top_rows
    ]
    values = [float(row["product_revenue"]) for row in top_rows]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(labels, values)
    ax.set_title("Top Product Category by Revenue in the 10 Highest-Revenue States")
    ax.set_xlabel("Product revenue (BRL)")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()

    save_chart(fig, "02_top_categories_by_state.png")


def chart_rolling_orders(rows):
    dates = [row["order_date"] for row in rows]
    daily = [int(row["order_count"]) for row in rows]
    rolling = [float(row["rolling_7day_avg_orders"]) for row in rows]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(dates, daily, linewidth=0.8, alpha=0.5, label="Daily orders")
    ax.plot(dates, rolling, linewidth=2, label="7-day rolling average")
    ax.set_title("Daily Order Demand and 7-Day Rolling Average")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of orders")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()

    save_chart(fig, "03_rolling_7day_orders.png")


def chart_delivery_reviews(rows):
    labels = [row["delivery_status"] for row in rows]
    scores = [
        float(row["average_review_score"])
        if row["average_review_score"] is not None else 0
        for row in rows
    ]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    bars = ax.bar(labels, scores)
    ax.set_title("Customer Review Score by Delivery Performance")
    ax.set_xlabel("Delivery status")
    ax.set_ylabel("Average review score (out of 5)")
    ax.set_ylim(0, 5)
    ax.grid(axis="y", alpha=0.3)

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.08,
            f"{score:.2f}",
            ha="center",
        )

    fig.tight_layout()
    save_chart(fig, "04_delivery_reviews.png")


def main():
    engine = get_engine()

    try:
        with engine.connect() as connection:
            monthly_rows = fetch_rows(
                connection, QUERIES["monthly_revenue"]
            )
            category_rows = fetch_rows(
                connection, QUERIES["top_categories"]
            )
            rolling_rows = fetch_rows(
                connection, QUERIES["rolling_orders"]
            )
            delivery_rows = fetch_rows(
                connection, QUERIES["delivery_reviews"]
            )

        if not all([
            monthly_rows,
            category_rows,
            rolling_rows,
            delivery_rows,
        ]):
            raise ValueError("At least one chart query returned no rows.")

        chart_monthly_revenue(monthly_rows)
        chart_top_categories(category_rows)
        chart_rolling_orders(rolling_rows)
        chart_delivery_reviews(delivery_rows)

        print("\nAll four charts generated successfully.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
