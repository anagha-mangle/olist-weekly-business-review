# Olist Marketplace - Weekly Business Review



## Overview



This project builds an analytics pipeline using the Olist Brazilian E-Commerce Public Dataset. It ingests raw CSV files into PostgreSQL, creates typed staging tables, runs data-quality checks, builds an analysis-ready mart, and produces SQL-based business metrics and a PDF business review.



## Architecture


Raw CSVs -> Raw PostgreSQL schema -> Staging schema -> Data quality gate -> Mart -> SQL analysis -> Charts -> PDF report


## Tech stack



\- Python 3.11

\- PostgreSQL 17

\- SQLAlchemy and psycopg

\- pandas for CSV ingestion and data preparation

\- Matplotlib for charts

\- ReportLab for the PDF report



## Key analyses



1\. Month-over-month delivered product revenue and growth using `LAG()`.

2\. Top three product categories by customer state using `DENSE\_RANK()`.

3\. Daily order demand and a seven-calendar-day rolling average.

4\. Repeat-purchase rate based on `customer\_unique\_id`.

5\. Delivery delay and average review score.



## Key findings



\- Delivered product revenue: R$13.22 million across 24 calendar months.

\- Repeat-purchase rate: 3.12% under the documented all-order definition.

\- Late-delivery rate: 8.11% among delivered orders with valid delivery-delay data.

\- Average review score: 2.57/5 for late deliveries versus 4.29/5 for early deliveries.



These results describe the historical dataset and should not be interpreted as current marketplace performance. The relationship between delivery timing and review scores is observational.



## Project structure



```text

.

├── data/

│   └── raw/                  # Downloaded CSVs; excluded from Git

├── reports/

│   ├── charts/               # Generated chart images

│   ├── vp\_memo.md

│   └── olist\_weekly\_business\_review.pdf

├── sql/

│   ├── 01\_mom\_revenue.sql

│   ├── 02\_top\_categories\_by\_state.sql

│   ├── 03\_rolling\_7day\_orders.sql

│   ├── 04\_repeat\_purchase\_rate.sql

│   ├── 05\_delivery\_delay\_reviews.sql

│   └── quality\_checks.sql

└── src/

&#x20;   ├── database.py

&#x20;   ├── ingest\_raw.py

&#x20;   ├── build\_staging\_\*.py

&#x20;   ├── run\_quality\_checks.py

&#x20;   ├── build\_mart.py

&#x20;   ├── generate\_charts.py

&#x20;   └── build\_report.py

```



## Setup



1\. Install Python 3.11 and PostgreSQL.

2\. Create a PostgreSQL database named `olist\_db`.

3\. Create the `raw`, `staging`, and `mart` schemas.

4\. Create a virtual environment and install the required packages.

5\. Copy `.env.example` to `.env` and configure the database connection locally.

6\. Download the Olist dataset and place the required CSVs in `data/raw/`.



Do not commit `.env` or database credentials.



## Running the pipeline



Run the scripts from the project root, in this order:



1\. `python .\\src\\ingest\_raw.py`

2\. Run the staging-table build scripts in `src/`.

3\. `python .\\src\\verify\_staging.py`

4\. `python .\\src\\run\_quality\_checks.py`

5\. `python .\\src\\build\_mart.py`

6\. Run the five SQL files against `olist\_db`.

7\. `python .\\src\\generate\_charts.py`

8\. `python .\\src\\build\_report.py`



The quality gate stops execution when a critical check fails. Documented warning-level anomalies are retained rather than silently modified.



## Data quality decisions



\- Duplicate review IDs are treated as warnings because repeated IDs occur across different orders; review records are retained.

\- Two payment records have zero installments; they are preserved and reported as warnings.

\- Missing product weights remain NULL rather than being imputed.

\- SQL checks validate duplicate keys, referential integrity, invalid scores, negative monetary values, missing purchase timestamps, and payment installment counts.



## Deliverables



\- Five SQL analysis queries

\- Data-quality SQL and Python gate

\- Four business charts

\- Four-page PDF business review



