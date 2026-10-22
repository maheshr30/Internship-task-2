"""
Task 2 - SQL for Business Questions
ApexPlanet Data Analytics Internship

1. Loads the cleaned CSV into a small SQLite star schema
   (fact_orders + dim_product + dim_city + dim_date).
2. Runs every query in sql/business_questions.sql.
3. Writes the queries and their results to sql/query_results.md.

Run from the repository root:
    python src/sql_analysis.py
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / "sql" / "sales_star_schema.db"
SQL_FILE = ROOT / "sql" / "business_questions.sql"
RESULTS = ROOT / "sql" / "query_results.md"

df = pd.read_csv(ROOT / "data" / "cleaned_sales_dataset.csv", parse_dates=["Order_Date"])

# ---------------------------------------------------------------- build schema
if DB_FILE.exists():
    DB_FILE.unlink()
con = sqlite3.connect(DB_FILE)

dim_product = (df[["Product", "Category"]].drop_duplicates().sort_values("Product")
               .reset_index(drop=True))
dim_product.insert(0, "product_id", dim_product.index + 1)
dim_product.columns = ["product_id", "product", "category"]

# State is reference data added for this analysis (not in the source file).
STATE = {"Patna": "Bihar", "Gaya": "Bihar", "Kolkata": "West Bengal", "Mumbai": "Maharashtra",
         "Pune": "Maharashtra", "Delhi": "Delhi", "Hyderabad": "Telangana",
         "Bengaluru": "Karnataka", "Unknown": "Unknown"}
dim_city = pd.DataFrame({"city": sorted(df["City"].unique())})
dim_city.insert(0, "city_id", dim_city.index + 1)
dim_city["state"] = dim_city["city"].map(STATE)

dates = pd.date_range(df["Order_Date"].min(), df["Order_Date"].max(), freq="D")
dim_date = pd.DataFrame({
    "date_key": dates.strftime("%Y-%m-%d"),
    "year": dates.year,
    "quarter": "Q" + dates.quarter.astype(str),
    "year_month": dates.strftime("%Y-%m"),
    "day_name": dates.day_name(),
    "is_weekend": (dates.dayofweek >= 5).astype(int),
})

fact = (df.merge(dim_product, left_on=["Product", "Category"], right_on=["product", "category"])
          .merge(dim_city, left_on="City", right_on="city"))
fact = pd.DataFrame({
    "order_key": fact["Order_Key"],
    "order_date": fact["Order_Date"].dt.strftime("%Y-%m-%d"),
    "customer_id": fact["Customer_ID"],
    "age": fact["Age"],
    "age_group": fact["Age_Group"],
    "gender": fact["Gender"],
    "city_id": fact["city_id"],
    "product_id": fact["product_id"],
    "quantity": fact["Quantity"],
    "unit_price": fact["Unit_Price"],
    "total_sales": fact["Total_Sales"],
    "is_outlier": fact["Is_Sales_Outlier"].astype(int),
})
assert len(fact) == len(df), "Join changed the row count"

for name, frame in [("dim_product", dim_product), ("dim_city", dim_city),
                    ("dim_date", dim_date), ("fact_orders", fact)]:
    frame.to_sql(name, con, index=False)

# ---------------------------------------------------------------- run queries
text = SQL_FILE.read_text(encoding="utf-8")
blocks = re.split(r"^-- @Q(\d+): (.*)$", text, flags=re.M)[1:]   # [num, title, body, num, title, body...]

lines = ["# SQL Queries and Results", "",
         "Database: SQLite star schema built by `src/sql_analysis.py` "
         "(`fact_orders`, `dim_product`, `dim_city`, `dim_date`).", ""]
for i in range(0, len(blocks), 3):
    num, title, body = blocks[i], blocks[i + 1], blocks[i + 2].strip()
    result = pd.read_sql_query(body, con)
    lines += [f"## Q{num}. {title}", "", "```sql", body, "```", "", "**Result**", ""]
    cols = list(result.columns)
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "---|" * len(cols))
    for _, row in result.iterrows():
        cells = [f"{v:,.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v) for v in row]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    print(f"Q{num}: {title}\n{result.to_string(index=False)}\n")

RESULTS.write_text("\n".join(lines), encoding="utf-8")
con.close()
print("Wrote", RESULTS)
