-- ===========================================================================
-- Task 2 - SQL for Business Questions (SQLite dialect)
-- Schema: fact_orders joined to dim_product, dim_city, dim_date
-- ===========================================================================

-- @Q1: Top 5 products by revenue in the last 6 months of data
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

-- @Q2: Monthly revenue trend with month-over-month growth
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

-- @Q3: Revenue and share of total by product category
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

-- @Q4: City performance ranked within each state
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

-- @Q5: Top-selling category for each age group
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

-- @Q6: Weekend vs weekday demand, normalised per calendar day
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

-- @Q7: Revenue concentration by order-value decile
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
