"""
MySQL ETL Loader (Monday Coffee)
=================================
Loads validated CSVs into the MySQL 'monday_coffee' schema.
Idempotent: safe to re-run any time (truncates before loading).
Run: python src/etl/load_to_mysql.py
"""
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# 1. Configuration 
# We use URL.create to safely handle the '@' in your password
DB_USER = "root"
DB_PASS = "Data@Project2026"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "monday_coffee"

url = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(url)

RAW = "data/raw/"
TABLES = ["city_dim", "product_dim", "customer_dim", "sales_fact"]

def reset_tables():
    """Clear tables in child-first order so re-runs never duplicate data."""
    # Using engine.begin() ensures DDL statements like TRUNCATE commit properly in SQLAlchemy 2.0
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for t in TABLES:
            conn.execute(text(f"TRUNCATE TABLE {t}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    print("  Tables reset (idempotent reload).")

def load():
    # Verify connection
    with engine.connect() as conn:
        version = conn.execute(text('SELECT VERSION()')).scalar()
        print(f"Connected to MySQL {version}")

    # Load raw CSVs into Pandas
    cities    = pd.read_csv(RAW + "city.csv")
    products  = pd.read_csv(RAW + "products.csv")
    customers = pd.read_csv(RAW + "customers.csv")
    sales     = pd.read_csv(RAW + "sales.csv", parse_dates=["sale_date"])

    # Wipe existing data
    reset_tables()

    # Load parent tables first to respect foreign keys
    print("  Loading city_dim...")
    cities.to_sql("city_dim", engine, if_exists="append", index=False, chunksize=500)
    
    print("  Loading product_dim...")
    products.to_sql("product_dim", engine, if_exists="append", index=False, chunksize=500)
    
    print("  Loading customer_dim...")
    customers.to_sql("customer_dim", engine, if_exists="append", index=False, chunksize=500)
    
    print("  Loading sales_fact...")
    sales.to_sql("sales_fact", engine, if_exists="append", index=False, chunksize=1000)

    # Verification
    print("\nLoad verification:")
    with engine.connect() as conn:
        for t in TABLES:
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"  {t:<14} {n:>7,} rows")
    print("\nETL complete.")

if __name__ == "__main__":
    load()