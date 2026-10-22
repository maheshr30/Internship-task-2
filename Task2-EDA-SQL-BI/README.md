# Task 2 - Exploratory Data Analysis (EDA) & Business Intelligence

ApexPlanet Software Pvt. Ltd. | Data Analytics Internship | Author: Mahesh R

## Objective
Uncover patterns, trends and relationships in the cleaned sales data (from Task 1), answer business questions with SQL, and propose a KPI dashboard.

## Deliverables
| Requirement | Where |
|---|---|
| EDA report | [`reports/EDA_Report.md`](reports/EDA_Report.md) (+ [`reports/statistics_tables.md`](reports/statistics_tables.md)) |
| SQL queries with results | [`sql/business_questions.sql`](sql/business_questions.sql), [`sql/query_results.md`](sql/query_results.md) |
| Descriptive statistics and univariate charts | `figures/fig01`, `fig02` |
| Multivariate analysis (scatter, heatmaps, pair plot) | `figures/fig05` - `fig10` |
| Static dashboard mock-up | [`dashboard/Dashboard_Mockup.pptx`](dashboard/Dashboard_Mockup.pptx) |

## Highlights
- Electronics generates **36.4%** of revenue (two products: Mobile and Laptop).
- **Mobile revenue fell 35%** from H1 to H2 2025, while Shoes (+28%) and Chair (+16%) grew.
- The top 10% of orders bring in **27.6%** of revenue.
- Q3 is the weakest quarter; August fell 19.6% month over month, then October rebounded 36.2%.
- Order value depends about equally on unit price (r = 0.69) and quantity (r = 0.65); age has no relationship with spend.

## SQL
Seven business questions are answered on a small SQLite star schema (`fact_orders` joined to `dim_product`, `dim_city`, `dim_date`) using joins, CTEs and window functions (LAG, RANK, NTILE). The database is built by `src/sql_analysis.py` and also saved as `sql/sales_star_schema.db`.

## How to run
```bash
pip install -r requirements.txt
python src/eda_analysis.py      # statistics + figures
python src/sql_analysis.py      # builds SQLite DB, runs queries, writes results
```

## Structure
```
data/cleaned_sales_dataset.csv   (output of Task 1)
src/eda_analysis.py   src/sql_analysis.py
sql/  reports/  figures/  dashboard/  docs/
```
