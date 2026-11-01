"""
Monday Coffee - Executive Terminal Dashboard
=============================================
Run: python src/analytics/executive_dashboard.py
"""
import pandas as pd

def main():
    scores = pd.read_csv("outputs/tables/city_expansion_scores.csv")
    products = pd.read_csv("outputs/tables/top_products.csv")
    
    top_city = scores.iloc[0]
    
    print("\n" + "="*80)
    print(" 🚀 MONDAY COFFEE: EXECUTIVE EXPANSION DASHBOARD 🚀")
    print("="*80)
    
    print(f"\n 🏆 PRIMARY EXPANSION TARGET: {top_city['city_name'].upper()}")
    print(f"    • Expansion Score: {top_city['expansion_score']}/100")
    print(f"    • Total Revenue:   ₹{top_city['total_revenue']:,.0f}")
    print(f"    • Revenue/Rent:    {top_city['revenue_per_rent']}x (Industry Benchmark: >50x)")
    print(f"    • Avg Rating:      {top_city['avg_rating']}/5.0")
    
    print("\n" + "-"*80)
    print(" 📈 TOP 3 MARKETS BY EXPANSION SCORE")
    print("-"*80)
    for i, row in scores.head(3).iterrows():
        print(f"  {i+1}. {row['city_name']:<12} | Score: {row['expansion_score']:<5} | Rev: ₹{row['total_revenue']:>9,.0f} | Rating: {row['avg_rating']}")
        
    print("\n" + "-"*80)
    print(" ☕ TOP REVENUE DRIVERS (Products)")
    print("-"*80)
    for i, row in products.head(3).iterrows():
        print(f"  • {row['product_name']:<35} | ₹{row['total_revenue']:>9,.0f}")
        
    print("\n" + "="*80)
    print(" 💡 STRATEGIC TAKEAWAY:")
    print("    Pune offers the highest risk-adjusted return. High rent efficiency")
    print("    and positive rating drift indicate a scalable, satisfied market.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()