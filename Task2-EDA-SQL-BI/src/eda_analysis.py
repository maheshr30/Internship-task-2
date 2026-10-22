"""
Task 2 - Exploratory Data Analysis (EDA)
ApexPlanet Data Analytics Internship

Produces descriptive statistics, univariate and multivariate charts from the
cleaned dataset created in Task 1.

Run from the repository root:
    python src/eda_analysis.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
REP = ROOT / "reports"
FIG.mkdir(exist_ok=True)
REP.mkdir(exist_ok=True)

df = pd.read_csv(ROOT / "data" / "cleaned_sales_dataset.csv", parse_dates=["Order_Date"])

sns.set_theme(style="whitegrid", font_scale=0.95)
PAL = "viridis"
BLUE = "#2f5d8a"


def savefig(name):
    plt.tight_layout()
    plt.savefig(FIG / name, dpi=140, bbox_inches="tight")
    plt.close()


def md_table(frame, floatfmt="{:,.2f}"):
    """Small DataFrame -> markdown helper (avoids the tabulate dependency)."""
    cols = [frame.index.name or ""] + list(map(str, frame.columns))
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for idx, row in frame.iterrows():
        cells = [str(idx)] + [floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v) for v in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------- 1. DESCRIPTIVE STATISTICS
num_cols = ["Age", "Quantity", "Unit_Price", "Total_Sales"]
desc = df[num_cols].describe().T
desc["skew"] = df[num_cols].skew()
desc["median"] = df[num_cols].median()
desc = desc[["count", "mean", "median", "std", "min", "25%", "75%", "max", "skew"]]
desc["count"] = desc["count"].astype(int)

cat_summary = {}
for c in ["Product", "Category", "City", "Gender", "Age_Group", "Order_Size", "Order_Quarter"]:
    vc = df[c].value_counts()
    cat_summary[c] = pd.DataFrame({"Orders": vc, "Share_%": (vc / len(df) * 100).round(1)})

rev_by = {}
for c in ["Category", "Product", "City", "Age_Group", "Gender", "Order_Quarter", "Order_Day_Of_Week"]:
    g = df.groupby(c).agg(Orders=("Order_Key", "count"), Revenue=("Total_Sales", "sum"),
                          Avg_Order_Value=("Total_Sales", "mean"))
    g["Revenue_Share_%"] = g["Revenue"] / g["Revenue"].sum() * 100
    rev_by[c] = g.sort_values("Revenue", ascending=False)

monthly = (df.assign(Month=df["Order_Date"].dt.to_period("M").astype(str))
             .groupby("Month").agg(Orders=("Order_Key", "count"), Revenue=("Total_Sales", "sum"),
                                   AOV=("Total_Sales", "mean")))

out = ["# Auto-generated statistics tables\n", "## Numeric summary\n", md_table(desc), ""]
for c, t in cat_summary.items():
    out += [f"## Orders by {c}\n", md_table(t, "{:,.1f}"), ""]
for c, t in rev_by.items():
    out += [f"## Revenue by {c}\n", md_table(t), ""]
out += ["## Monthly trend\n", md_table(monthly)]
(REP / "statistics_tables.md").write_text("\n".join(out), encoding="utf-8")

# ---------------------------------------------------------------- 2. UNIVARIATE CHARTS
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
sns.histplot(df["Age"], bins=24, color=BLUE, ax=ax[0, 0]).set_title("Age distribution")
sns.histplot(df["Quantity"], bins=10, discrete=True, color=BLUE, ax=ax[0, 1]).set_title("Quantity per order")
sns.histplot(df["Unit_Price"], bins=30, color=BLUE, ax=ax[1, 0]).set_title("Unit price distribution")
sns.histplot(df["Total_Sales"], bins=40, color=BLUE, ax=ax[1, 1]).set_title("Order value (Total_Sales) - right-skewed")
savefig("fig01_numeric_distributions.png")

fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for a, (col, order) in zip(ax.ravel(), [("Product", None), ("City", None), ("Gender", None),
                                         ("Age_Group", ["18-25", "26-35", "36-45", "46-55", "56-65"])]):
    sns.countplot(data=df, x=col, order=order or df[col].value_counts().index, color=BLUE, ax=a)
    a.set_title(f"Orders by {col}")
    a.tick_params(axis="x", rotation=30)
    a.set_xlabel("")
savefig("fig02_categorical_counts.png")

# ---------------------------------------------------------------- 3. REVENUE CHARTS
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(monthly.index, monthly["Revenue"] / 1e6, marker="o", color=BLUE)
ax.set_title("Monthly revenue (millions)")
ax.set_ylabel("Revenue (M)")
ax.tick_params(axis="x", rotation=45)
savefig("fig03_monthly_revenue.png")

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
c = rev_by["Category"]["Revenue"] / 1e6
ax[0].barh(c.index[::-1], c.values[::-1], color=BLUE)
ax[0].set_title("Revenue by category (M)")
ci = rev_by["City"]["Revenue"] / 1e6
ax[1].barh(ci.index[::-1], ci.values[::-1], color=BLUE)
ax[1].set_title("Revenue by city (M)")
savefig("fig04_revenue_category_city.png")

# ---------------------------------------------------------------- 4. MULTIVARIATE
corr = df[num_cols].corr()
plt.figure(figsize=(5.5, 4.5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, square=True)
plt.title("Correlation matrix")
savefig("fig05_correlation_heatmap.png")

fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
sns.scatterplot(data=df, x="Quantity", y="Total_Sales", hue="Category", palette="deep", alpha=0.7, ax=ax[0])
ax[0].set_title("Quantity vs order value")
sns.scatterplot(data=df, x="Age", y="Total_Sales", hue="Category", palette="deep", alpha=0.7, ax=ax[1], legend=False)
ax[1].set_title("Age vs order value")
savefig("fig06_scatter_plots.png")

pp = sns.pairplot(df[num_cols + ["Category"]], hue="Category", palette="deep", corner=True,
                  plot_kws={"alpha": 0.5, "s": 18}, height=2.0)
pp.savefig(FIG / "fig07_pairplot.png", dpi=110)
plt.close("all")

pivot = df.pivot_table(index="City", columns="Category", values="Total_Sales", aggfunc="sum") / 1e6
plt.figure(figsize=(8, 5))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={"label": "Revenue (M)"})
plt.title("Revenue (M) by city and category")
savefig("fig08_city_category_heatmap.png")

plt.figure(figsize=(8, 4.5))
sns.boxplot(data=df, x="Product", y="Unit_Price", color="#9db8d3")
plt.title("Unit price by product - ranges overlap heavily")
savefig("fig09_price_by_product.png")

pivot_age = df.pivot_table(index="Age_Group", columns="Category", values="Total_Sales", aggfunc="sum") / 1e6
plt.figure(figsize=(8, 4))
sns.heatmap(pivot_age, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={"label": "Revenue (M)"})
plt.title("Revenue (M) by age group and category")
savefig("fig10_agegroup_category_heatmap.png")

half = np.where(df["Order_Date"] >= pd.Timestamp("2025-07-01"), "H2 (Jul-Jan 1)", "H1 (Jan-Jun)")
ph = df.assign(Half=half).pivot_table(index="Product", columns="Half", values="Total_Sales", aggfunc="sum") / 1e6
ph["Change_%"] = (ph["H2 (Jul-Jan 1)"] / ph["H1 (Jan-Jun)"] - 1) * 100
ph = ph.sort_values("Change_%")
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(ph.index, ph["Change_%"], color=["#c0504d" if v < 0 else BLUE for v in ph["Change_%"]])
ax.axvline(0, color="grey", lw=0.8)
ax.set_title("Product revenue change, H2 vs H1 (%)")
for i, v in enumerate(ph["Change_%"]):
    ax.text(v + (1 if v >= 0 else -1), i, f"{v:+.0f}%", va="center", ha="left" if v >= 0 else "right")
ax.set_xlim(ph["Change_%"].min() - 12, ph["Change_%"].max() + 12)
savefig("fig11_product_h1_vs_h2.png")
(REP / "statistics_tables.md").write_text(
    (REP / "statistics_tables.md").read_text(encoding="utf-8")
    + "\n\n## Product revenue, H1 vs H2 (millions)\n\n" + md_table(ph), encoding="utf-8")

# ---------------------------------------------------------------- 5. KEY NUMBERS (console)
print(desc.round(2).to_string())
print("\nCorrelations:\n", corr.round(3).to_string())
for k in ["Category", "Product", "City", "Age_Group", "Gender", "Order_Quarter", "Order_Day_Of_Week"]:
    print(f"\nRevenue by {k}:\n", rev_by[k].round(1).to_string())
print("\nMonthly:\n", monthly.round(0).to_string())
top = df.nlargest(int(len(df) * 0.05), "Total_Sales")["Total_Sales"].sum() / df["Total_Sales"].sum()
print(f"\nTop 5% of orders = {top:.1%} of revenue; outlier orders = {df.Is_Sales_Outlier.sum()}, "
      f"{df.loc[df.Is_Sales_Outlier,'Total_Sales'].sum()/df.Total_Sales.sum():.1%} of revenue")
print("Weekend share of orders:", round(df.Is_Weekend.mean() * 100, 1), "%")
print("Price corr by product (medians):\n", df.groupby("Product").Unit_Price.median().round(0).to_string())
print("EDA complete. Figures in", FIG)
