"""
Monday Coffee - Production Data Quality Audit
==============================================
Run: python src/etl/profile_data.py
Purpose: Validate data integrity BEFORE loading to PostgreSQL
"""
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path("data/raw")

def load_data():
    """Load all CSVs with explicit dtypes"""
    cities = pd.read_csv(RAW / "city.csv")
    customers = pd.read_csv(RAW / "customers.csv")
    products = pd.read_csv(RAW / "products.csv")
    sales = pd.read_csv(RAW / "sales.csv", parse_dates=["sale_date"])
    return cities, customers, products, sales

def audit_data(cities, customers, products, sales):
    """Comprehensive data quality checks"""
    print("=" * 70)
    print("MONDAY COFFEE - DATA QUALITY AUDIT REPORT")
    print("=" * 70)
    
    # 1. Volume & Coverage
    print("\n1. DATA VOLUME & TEMPORAL COVERAGE")
    print("-" * 70)
    tables = {"cities": cities, "customers": customers, "products": products, "sales": sales}
    for name, df in tables.items():
        print(f"  {name:<12} {len(df):>7,} rows   {df.shape[1]} cols")
    
    span = (sales.sale_date.max() - sales.sale_date.min()).days
    print(f"\n  Sales window: {sales.sale_date.min():%Y-%m-%d} → {sales.sale_date.max():%Y-%m-%d}")
    print(f"  Duration: {span // 30} months ({span} days)")
    
    # 2. Integrity Checks
    print("\n2. REFERENTIAL INTEGRITY CHECKS")
    print("-" * 70)
    orphan_sales_prod = (~sales.product_id.isin(products.product_id)).sum()
    orphan_sales_cust = (~sales.customer_id.isin(customers.customer_id)).sum()
    orphan_cust_city = (~customers.city_id.isin(cities.city_id)).sum()
    
    print(f"  Orphan sales → products:  {orphan_sales_prod:,} {'❌ FAIL' if orphan_sales_prod else '✅ PASS'}")
    print(f"  Orphan sales → customers: {orphan_sales_cust:,} {'❌ FAIL' if orphan_sales_cust else '✅ PASS'}")
    print(f"  Orphan customers → city:  {orphan_cust_city:,} {'❌ FAIL' if orphan_cust_city else '✅ PASS'}")
    
    # 3. Data Quality Flags
    print("\n3. DATA QUALITY FLAGS")
    print("-" * 70)
    total_nulls = sum(df.isna().sum().sum() for df in [cities, customers, products, sales])
    print(f"  Total NULL values: {total_nulls:,} {'⚠️  WARNING' if total_nulls else '✅ PASS'}")
    
    # Price consistency
    chk = sales.merge(products[["product_id", "price"]], on="product_id", how="left")
    price_mismatch = (chk["total"] != chk["price"]).sum()
    print(f"  Sales total ≠ listed price: {price_mismatch:,} {'❌ FAIL' if price_mismatch else '✅ PASS'}")
    
    # Duplicates
    dup_customers = customers.customer_name.duplicated().sum()
    print(f"  Duplicate customer names: {dup_customers:,} {'⚠️  WARNING' if dup_customers else '✅ PASS'}")
    
    # Rating range
    print(f"  Rating range: {sales.rating.min()} - {sales.rating.max()} {'✅ VALID' if sales.rating.between(1, 5).all() else '❌ INVALID'}")
    
    # 4. City League Table
    print("\n4. CITY PERFORMANCE LEAGUE TABLE")
    print("-" * 70)
    rich = sales.merge(customers, on="customer_id").merge(cities, on="city_id")
    league = (
        rich.groupby("city_name")
        .agg(revenue=("total", "sum"),
             orders=("sale_id", "count"),
             buyers=("customer_id", "nunique"),
             avg_rating=("rating", "mean"))
        .join(cities.set_index("city_name")[["population", "estimated_rent", "city_rank"]])
    )
    league["rev_per_customer"] = (league.revenue / league.buyers).round(0)
    league["rev_per_rent"] = (league.revenue / league.estimated_rent).round(1)
    league["avg_rating"] = league.avg_rating.round(2)
    print(league.sort_values("revenue", ascending=False).to_string())
    
    # 5. Rating Drift Analysis (Hidden Story)
    print("\n5. CUSTOMER SATISFACTION DRIFT (H1 vs H2)")
    print("-" * 70)
    mid = rich.sale_date.median()
    rich = rich.assign(half=(rich.sale_date > mid).map({False: "H1", True: "H2"}))
    pivot = rich.groupby(["city_name", "half"]).rating.mean().unstack().round(2)
    pivot["drift"] = (pivot["H2"] - pivot["H1"]).round(2)
    print(pivot.sort_values("drift").to_string())
    
    # 6. Monthly Momentum
    print("\n6. MONTHLY REVENUE MOMENTUM (Last 6 Months)")
    print("-" * 70)
    monthly = rich.groupby(rich.sale_date.dt.to_period("M")).total.sum()
    print(monthly.tail(6).to_string())
    
    # 7. Recommendations
    print("\n7. PRELIMINARY EXPANSION CANDIDATES")
    print("-" * 70)
    candidates = league.sort_values(["revenue", "rev_per_rent", "avg_rating"], 
                                    ascending=[False, False, False]).head(3)
    for city in candidates.index:
        row = candidates.loc[city]
        print(f"  ✓ {city:<15} Revenue: ₹{row.revenue:,.0f} | Rev/Rent: {row.rev_per_rent:.0f} | Rating: {row.avg_rating:.2f}")
    
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)
    
    return league, pivot

if __name__ == "__main__":
    cities, customers, products, sales = load_data()
    league, drift = audit_data(cities, customers, products, sales)
    
    # Save audit outputs
    Path("data/processed").mkdir(exist_ok=True)
    league.to_csv("data/processed/city_league_table.csv")
    drift.to_csv("data/processed/rating_drift_analysis.csv")
    print("\n✓ Audit results saved to data/processed/")