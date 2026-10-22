# SQL Queries and Results

Database: SQLite star schema built by `src/sql_analysis.py` (`fact_orders`, `dim_product`, `dim_city`, `dim_date`).

## Q1. Top 5 products by revenue in the last 6 months of data

```sql
-- Business question: Which products drove the most revenue recently?
-- Skills: filtering (relative date), aggregation, join
SELECT p.product,
       p.category,
       COUNT(*)                          AS orders,
       SUM(f.quantity)                   AS units_sold,
       ROUND(SUM(f.total_sales), 2)      AS revenue
FROM fact_orders f
JOIN dim_product p ON p.product_id = f.product_id
WHERE f.order_date >= (SELECT DATE(MAX(order_date), '-6 months') FROM fact_orders)
GROUP BY p.product, p.category
ORDER BY revenue DESC
LIMIT 5;
```

**Result**

| product | category | orders | units_sold | revenue |
|---|---|---|---|---|
| Laptop | Electronics | 88 | 501 | 13,009,494.74 |
| Book | Education | 92 | 542 | 12,739,832.53 |
| Chair | Furniture | 87 | 467 | 11,560,952.45 |
| Shoes | Fashion | 81 | 453 | 11,149,392.03 |
| Rice | Grocery | 75 | 394 | 10,215,563.97 |

## Q2. Monthly revenue trend with month-over-month growth

```sql
-- Business question: How is revenue trending, and which months dipped?
-- Skills: join to date dimension, aggregation, LAG window function
-- Note: 2026-01 contains only the 1st of the month (partial month).
WITH monthly AS (
    SELECT d.year_month,
           COUNT(*)                       AS orders,
           SUM(f.total_sales)             AS revenue
    FROM fact_orders f
    JOIN dim_date d ON d.date_key = f.order_date
    GROUP BY d.year_month
)
SELECT year_month,
       orders,
       ROUND(revenue, 0)                                              AS revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY year_month))
             * 100.0 / LAG(revenue) OVER (ORDER BY year_month), 1)    AS mom_growth_pct
FROM monthly
ORDER BY year_month;
```

**Result**

| year_month | orders | revenue | mom_growth_pct |
|---|---|---|---|
| 2025-01 | 76 | 10,096,191 | nan |
| 2025-02 | 86 | 11,511,181 | 14 |
| 2025-03 | 89 | 13,059,900 | 13.5 |
| 2025-04 | 80 | 12,222,700 | -6.4 |
| 2025-05 | 85 | 10,984,689 | -10.1 |
| 2025-06 | 83 | 12,912,333 | 17.5 |
| 2025-07 | 83 | 11,746,227 | -9 |
| 2025-08 | 75 | 9,448,471 | -19.6 |
| 2025-09 | 79 | 9,179,896 | -2.8 |
| 2025-10 | 84 | 12,500,937 | 36.2 |
| 2025-11 | 77 | 12,627,620 | 1 |
| 2025-12 | 98 | 12,299,904 | -2.6 |
| 2026-01 | 5 | 809,390 | -93.4 |

## Q3. Revenue and share of total by product category

```sql
-- Business question: Which categories matter most to the business?
-- Skills: join, aggregation, window SUM() OVER ()
SELECT p.category,
       COUNT(*)                                                       AS orders,
       ROUND(SUM(f.total_sales), 0)                                   AS revenue,
       ROUND(AVG(f.total_sales), 0)                                   AS avg_order_value,
       ROUND(SUM(f.total_sales) * 100.0 / SUM(SUM(f.total_sales)) OVER (), 1) AS revenue_share_pct
FROM fact_orders f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.category
ORDER BY revenue DESC;
```

**Result**

| category | orders | revenue | avg_order_value | revenue_share_pct |
|---|---|---|---|---|
| Electronics | 354 | 50,778,582 | 143,442 | 36.4 |
| Education | 178 | 25,031,689 | 140,627 | 18 |
| Grocery | 153 | 22,231,711 | 145,305 | 15.9 |
| Furniture | 159 | 21,521,561 | 135,356 | 15.4 |
| Fashion | 156 | 19,835,896 | 127,153 | 14.2 |

## Q4. City performance ranked within each state

```sql
-- Business question: Which cities lead their state, and where is order value highest?
-- Skills: 3-table join, aggregation, RANK() OVER (PARTITION BY ...)
SELECT c.state,
       c.city,
       COUNT(*)                                                       AS orders,
       ROUND(SUM(f.total_sales), 0)                                   AS revenue,
       ROUND(AVG(f.total_sales), 0)                                   AS avg_order_value,
       RANK() OVER (PARTITION BY c.state ORDER BY SUM(f.total_sales) DESC) AS rank_in_state
FROM fact_orders f
JOIN dim_city c ON c.city_id = f.city_id
WHERE c.city <> 'Unknown'
GROUP BY c.state, c.city
ORDER BY c.state, rank_in_state;
```

**Result**

| state | city | orders | revenue | avg_order_value | rank_in_state |
|---|---|---|---|---|---|
| Bihar | Patna | 135 | 19,285,967 | 142,859 | 1 |
| Bihar | Gaya | 117 | 14,380,859 | 122,913 | 2 |
| Delhi | Delhi | 125 | 16,097,079 | 128,777 | 1 |
| Karnataka | Bengaluru | 122 | 18,773,574 | 153,882 | 1 |
| Maharashtra | Mumbai | 131 | 18,757,050 | 143,184 | 1 |
| Maharashtra | Pune | 99 | 14,513,176 | 146,598 | 2 |
| Telangana | Hyderabad | 125 | 17,166,767 | 137,334 | 1 |
| West Bengal | Kolkata | 133 | 18,884,350 | 141,988 | 1 |

## Q5. Top-selling category for each age group

```sql
-- Business question: What does each age segment buy the most (by revenue)?
-- Skills: join, CTE, RANK() OVER (PARTITION BY ...)
WITH age_cat AS (
    SELECT f.age_group,
           p.category,
           SUM(f.total_sales) AS revenue
    FROM fact_orders f
    JOIN dim_product p ON p.product_id = f.product_id
    GROUP BY f.age_group, p.category
),
ranked AS (
    SELECT age_group, category, revenue,
           RANK() OVER (PARTITION BY age_group ORDER BY revenue DESC) AS rnk
    FROM age_cat
)
SELECT age_group, category AS top_category, ROUND(revenue, 0) AS revenue
FROM ranked
WHERE rnk = 1
ORDER BY age_group;
```

**Result**

| age_group | top_category | revenue |
|---|---|---|
| 18-25 | Electronics | 7,240,853 |
| 26-35 | Electronics | 12,268,938 |
| 36-45 | Electronics | 11,372,416 |
| 46-55 | Electronics | 10,385,266 |
| 56-65 | Electronics | 9,511,108 |

## Q6. Weekend vs weekday demand, normalised per calendar day

```sql
-- Business question: Do weekends sell more or less per day than weekdays?
-- Skills: LEFT JOIN from a full calendar table, conditional grouping
SELECT CASE WHEN d.is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
       COUNT(DISTINCT d.date_key)                                    AS calendar_days,
       COUNT(f.order_key)                                            AS orders,
       ROUND(COUNT(f.order_key) * 1.0 / COUNT(DISTINCT d.date_key), 2) AS orders_per_day,
       ROUND(SUM(f.total_sales) / COUNT(DISTINCT d.date_key), 0)     AS revenue_per_day,
       ROUND(AVG(f.total_sales), 0)                                  AS avg_order_value
FROM dim_date d
LEFT JOIN fact_orders f ON f.order_date = d.date_key
GROUP BY day_type
ORDER BY day_type DESC;
```

**Result**

| day_type | calendar_days | orders | orders_per_day | revenue_per_day | avg_order_value |
|---|---|---|---|---|---|
| Weekend | 104 | 288 | 2.77 | 368,953 | 133,233 |
| Weekday | 262 | 712 | 2.72 | 385,604 | 141,894 |

## Q7. Revenue concentration by order-value decile

```sql
-- Business question: How dependent is revenue on the biggest orders?
-- Skills: NTILE window function, CTE, cumulative share
WITH deciles AS (
    SELECT total_sales,
           NTILE(10) OVER (ORDER BY total_sales DESC) AS decile
    FROM fact_orders
)
SELECT decile,
       COUNT(*)                                                        AS orders,
       ROUND(SUM(total_sales), 0)                                      AS revenue,
       ROUND(SUM(total_sales) * 100.0 / SUM(SUM(total_sales)) OVER (), 1) AS revenue_share_pct,
       ROUND(SUM(SUM(total_sales)) OVER (ORDER BY decile) * 100.0
             / SUM(SUM(total_sales)) OVER (), 1)                       AS cumulative_share_pct
FROM deciles
GROUP BY decile
ORDER BY decile;
```

**Result**

| decile | orders | revenue | revenue_share_pct | cumulative_share_pct |
|---|---|---|---|---|
| 1 | 100 | 38,470,936 | 27.6 | 27.6 |
| 2 | 100 | 26,797,531 | 19.2 | 46.8 |
| 3 | 100 | 20,597,699 | 14.8 | 61.6 |
| 4 | 100 | 15,866,442 | 11.4 | 73 |
| 5 | 100 | 12,379,967 | 8.9 | 81.9 |
| 6 | 100 | 9,719,660 | 7 | 88.8 |
| 7 | 100 | 7,296,888 | 5.2 | 94.1 |
| 8 | 100 | 4,641,167 | 3.3 | 97.4 |
| 9 | 100 | 2,722,302 | 2 | 99.3 |
| 10 | 100 | 906,849 | 0.7 | 100 |
