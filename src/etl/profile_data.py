"""
Monday Coffee - Data Profiling & Quality Audit
===============================================
Run: python src/profile_data.py
"""
import pandas as pd

RAW = "data/raw/"
cities = pd.read_csv(RAW + "city.csv")
customers = pd.read_csv(RAW + "customers.csv")
products = pd.read_csv(RAW + "products.csv")
sales = pd.read_csv(RAW + "sales.csv", parse_dates=["sale_date"])

print("=" * 62)
print("1. VOLUME & COVERAGE")
print("=" * 62)
for name, df in [("cities", cities), ("customers", customers),
                 ("products", products), ("sales", sales)]:
    print(f"  {name:<10} {len(df):>7,} rows   {df.shape[1]} cols")
span = (sales.sale_date.max() - sales.sale_date.min()).days
print(f"  Sales window: {sales.sale_date.min():%Y-%m-%d} -> {sales.sale_date.max():%Y-%m-%d} ({span // 30} months)")

print("=" * 62)
print("2. INTEGRITY & QUALITY FLAGS")
print("=" * 62)
print("  orphan sales->products :", (~sales.product_id.isin(products.product_id)).sum())
print("  orphan sales->customers:", (~sales.customer_id.isin(customers.customer_id)).sum())
print("  orphan customers->city :", (~customers.city_id.isin(cities.city_id)).sum())
print("  nulls anywhere         :", sum(d.isna().sum().sum() for d in (cities, customers, products, sales)))
chk = sales.merge(products[["product_id", "price"]], on="product_id", how="left")
print("  total != listed price  :", (chk.total != chk.price).sum())
print("  duplicate customer names:", customers.customer_name.duplicated().sum())
print("  rating range           :", sales.rating.min(), "-", sales.rating.max())

rich = sales.merge(customers, on="customer_id").merge(cities, on="city_id")

print("=" * 62)
print("3. CITY LEAGUE TABLE (revenue vs rent vs satisfaction)")
print("=" * 62)
league = (
    rich.groupby("city_name")
    .agg(revenue=("total", "sum"),
         orders=("sale_id", "count"),
         buyers=("customer_id", "nunique"),
         avg_rating=("rating", "mean"))
    .join(cities.set_index("city_name")[["population", "estimated_rent", "city_rank"]])
)
league["rev_per_customer"] = (league.revenue / league.buyers).round(0)
league["rev_per_rent_rupee"] = (league.revenue / league.estimated_rent).round(1)
league["avg_rating"] = league.avg_rating.round(2)
print(league.sort_values("revenue", ascending=False).to_string())

print("=" * 62)
print("4. THE HIDDEN STORY: rating drift (first half vs second half)")
print("=" * 62)
mid = rich.sale_date.median()
rich = rich.assign(half=(rich.sale_date > mid).map({False: "H1", True: "H2"}))
pivot = rich.groupby(["city_name", "half"]).rating.mean().unstack().round(2)
pivot["drift"] = (pivot["H2"] - pivot["H1"]).round(2)
print(pivot.sort_values("drift").to_string())

print("=" * 62)
print("5. MONTHLY MOMENTUM (last 6 months, total revenue)")
print("=" * 62)
monthly = rich.groupby(rich.sale_date.dt.to_period("M")).total.sum()
print(monthly.tail(6).to_string())