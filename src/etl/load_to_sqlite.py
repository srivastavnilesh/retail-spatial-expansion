"""
SQLite ETL Loader (Monday Coffee)
=================================
Zero-configuration database loader. No passwords, no servers, no errors.
Run: python src/etl/load_to_sqlite.py
"""
import pandas as pd
import sqlite3
from pathlib import Path

# This creates a database file directly in your project folder
DB_NAME = "data/processed/monday_coffee.db"
RAW = "data/raw/"
TABLES = ["city_dim", "product_dim", "customer_dim", "sales_fact"]

def load():
    # Ensure the output directory exists
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    # Connect to SQLite (this automatically creates the file)
    conn = sqlite3.connect(DB_NAME)
    print(f"Connected to SQLite database at {DB_NAME}")

    # Load CSVs
    cities    = pd.read_csv(RAW + "city.csv")
    products  = pd.read_csv(RAW + "products.csv")
    customers = pd.read_csv(RAW + "customers.csv")
    sales     = pd.read_csv(RAW + "sales.csv", parse_dates=["sale_date"])

    # Write to SQLite (if_exists="replace" automatically drops and recreates tables)
    print("  Loading city_dim...")
    cities.to_sql("city_dim", conn, if_exists="replace", index=False)
    
    print("  Loading product_dim...")
    products.to_sql("product_dim", conn, if_exists="replace", index=False)
    
    print("  Loading customer_dim...")
    customers.to_sql("customer_dim", conn, if_exists="replace", index=False)
    
    print("  Loading sales_fact...")
    sales.to_sql("sales_fact", conn, if_exists="replace", index=False)

    # Verification
    print("\nLoad verification:")
    for t in TABLES:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<14} {n:>7,} rows")
        
    conn.close()
    print("\nETL complete. Database file saved to data/processed/monday_coffee.db")

if __name__ == "__main__":
    load()