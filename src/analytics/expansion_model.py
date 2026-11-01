"""
Monday Coffee - Expansion Recommendation Engine
================================================
Analyzes SQL views to score cities and predict expansion ROI.
Run: python src/analytics/expansion_model.py
"""
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = "data/processed/monday_coffee.db"

def load_views():
    """Load all SQL views into pandas DataFrames"""
    conn = sqlite3.connect(DB_PATH)
    
    city_perf = pd.read_sql("SELECT * FROM v_city_performance", conn)
    momentum = pd.read_sql("SELECT * FROM v_monthly_momentum", conn)
    products = pd.read_sql("SELECT * FROM v_product_profitability", conn)
    customers = pd.read_sql("SELECT * FROM v_customer_segments", conn)
    drift = pd.read_sql("SELECT * FROM v_rating_drift", conn)
    
    conn.close()
    return city_perf, momentum, products, customers, drift

def calculate_expansion_score(city_perf, drift):
    """
    Weighted scoring model for expansion candidates.
    
    Weights:
    - Revenue per Rent (40%): Efficiency metric - how much revenue per rupee of rent
    - Average Rating (30%): Customer satisfaction - critical for retention
    - Total Revenue (20%): Market validation - proven demand
    - Rating Drift (10%): Trend direction - positive drift = improving
    """
    # Merge city performance with rating drift
    df = city_perf.merge(drift[['city_name', 'rating_drift']], on='city_name', how='left')
    
    # Normalize metrics to 0-100 scale
    df['rev_per_rent_norm'] = (df['revenue_per_rent'] / df['revenue_per_rent'].max()) * 100
    df['rating_norm'] = (df['avg_rating'] / 5) * 100
    df['revenue_norm'] = (df['total_revenue'] / df['total_revenue'].max()) * 100
    
    # Handle rating drift (can be negative)
    drift_min = df['rating_drift'].min()
    drift_max = df['rating_drift'].max()
    if drift_max > drift_min:
        df['drift_norm'] = ((df['rating_drift'] - drift_min) / (drift_max - drift_min)) * 100
    else:
        df['drift_norm'] = 50  # Neutral if no variation
    
    # Calculate weighted expansion score
    df['expansion_score'] = (
        df['rev_per_rent_norm'] * 0.40 +
        df['rating_norm'] * 0.30 +
        df['revenue_norm'] * 0.20 +
        df['drift_norm'] * 0.10
    ).round(1)
    
    return df.sort_values('expansion_score', ascending=False)

def analyze_top_products(products):
    """Identify top 5 products by revenue"""
    return products.nlargest(5, 'total_revenue')[['product_name', 'price', 'total_units_sold', 'total_revenue']]

def analyze_customer_segments(customers):
    """Breakdown of customer tiers"""
    return customers.groupby('customer_tier').agg(
        customer_count=('customer_id', 'count'),
        avg_lifetime_value=('lifetime_value', 'mean'),
        avg_orders=('total_orders', 'mean')
    ).round(2)

def generate_recommendations(scored_cities):
    """Generate top 3 expansion recommendations with justification"""
    top3 = scored_cities.head(3)
    
    print("\n" + "="*80)
    print("🎯 TOP 3 EXPANSION RECOMMENDATIONS")
    print("="*80)
    
    for idx, row in top3.iterrows():
        print(f"\n{idx+1}. {row['city_name'].upper()} (Score: {row['expansion_score']})")
        print(f"   └─ Revenue: ₹{row['total_revenue']:,.0f} | Rev/Rent: {row['revenue_per_rent']}")
        print(f"   └─ Rating: {row['avg_rating']}/5 | Drift: {row['rating_drift']:+.2f}")
        print(f"   └─ Customers: {row['unique_customers']} | Orders: {row['total_orders']}")
        
        # Strategic justification
        if row['revenue_per_rent'] > 70:
            print(f"   ✓ HIGH EFFICIENCY: Exceptional revenue-to-rent ratio")
        if row['avg_rating'] > 4.4:
            print(f"   ✓ STRONG SATISFACTION: Premium customer experience")
        if row['rating_drift'] > 0:
            print(f"   ✓ POSITIVE MOMENTUM: Customer satisfaction improving")
    
    return top3

def main():
    print("="*80)
    print("MONDAY COFFEE - EXPANSION ANALYTICS ENGINE")
    print("="*80)
    
    # Load data
    print("\n📊 Loading SQL views...")
    city_perf, momentum, products, customers, drift = load_views()
    print(f"  ✓ Loaded {len(city_perf)} cities, {len(products)} products, {len(customers)} customers")
    
    # Calculate expansion scores
    print("\n🎯 Calculating expansion scores...")
    scored_cities = calculate_expansion_score(city_perf, drift)
    
    # Generate recommendations
    top3 = generate_recommendations(scored_cities)
    
    # Product analysis
    print("\n" + "="*80)
    print("☕ TOP 5 PRODUCTS BY REVENUE")
    print("="*80)
    top_products = analyze_top_products(products)
    print(top_products.to_string(index=False))
    
    # Customer segment analysis
    print("\n" + "="*80)
    print("👥 CUSTOMER SEGMENT BREAKDOWN")
    print("="*80)
    segments = analyze_customer_segments(customers)
    print(segments.to_string())
    
    # Save outputs
    print("\n💾 Saving analytics outputs...")
    Path("outputs/tables").mkdir(parents=True, exist_ok=True)
    scored_cities.to_csv("outputs/tables/city_expansion_scores.csv", index=False)
    top_products.to_csv("outputs/tables/top_products.csv", index=False)
    segments.to_csv("outputs/tables/customer_segments.csv")
    
    print("\n" + "="*80)
    print("✅ ANALYTICS COMPLETE")
    print("="*80)
    print(f"\n📁 Outputs saved to outputs/tables/")
    print(f"   • city_expansion_scores.csv")
    print(f"   • top_products.csv")
    print(f"   • customer_segments.csv")
    print("\n🚀 Ready for Phase 4: Tableau Dashboard")

if __name__ == "__main__":
    main()