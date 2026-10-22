# LinkedIn Video Script (5-7 min)

| Time | Show | Say |
|------|------|-----|
| 0:00-0:30 | GitHub repo (Task 2) | "I'm Mahesh R. This is Task 2 of my ApexPlanet Data Analytics internship: exploratory data analysis, SQL and a dashboard mock-up, using the cleaned dataset from Task 1." |
| 0:30-1:30 | `figures/fig01`, `fig02` | Descriptive stats: age, quantity and price are evenly spread; order value is right-skewed (mean 139k vs median 109k). Orders are balanced across products, cities and gender. |
| 1:30-2:45 | `fig05` correlation heatmap, `fig06` scatter | Order value depends about equally on price (0.69) and quantity (0.65); they are independent of each other; age has no effect. |
| 2:45-4:30 | `sql/query_results.md` | Explain the star schema (fact + 3 dimensions). Walk through 3 queries: Q1 top products (Mobile missing from the top 5), Q2 month-over-month with LAG (Aug dip, Oct rebound), Q7 concentration with NTILE (top 10% of orders = 27.6% of revenue). Mention the partial January 2026 month. |
| 4:30-5:30 | `fig11` and EDA report insights | Electronics 36.4% (two products), Mobile down 35% H2 vs H1, Q3 dip, no weekend effect. |
| 5:30-6:30 | `Dashboard_Mockup.pptx` | Explain each KPI card and why it was chosen (revenue, orders, AOV, MoM growth, top-category share, top-10% order share) and the three charts. |
| 6:30-7:00 | Wrap-up | "Key learning: SQL window functions answer trend and ranking questions quickly. Next, Task 3: KPIs, a deep-dive segmentation and an interactive dashboard." |
