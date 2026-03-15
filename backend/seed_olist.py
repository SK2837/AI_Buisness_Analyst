"""
Loads Olist Brazilian E-Commerce CSVs into PostgreSQL.
Run from the backend/ directory with venv active:
    python seed_olist.py
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ai_business_analyst"
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

engine = create_engine(DATABASE_URL)

tables = {
    "olist_orders":        "olist_orders_dataset.csv",
    "olist_order_items":   "olist_order_items_dataset.csv",
    "olist_order_reviews": "olist_order_reviews_dataset.csv",
    "olist_order_payments":"olist_order_payments_dataset.csv",
    "olist_customers":     "olist_customers_dataset.csv",
    "olist_sellers":       "olist_sellers_dataset.csv",
    "olist_products":      "olist_products_dataset.csv",
    "olist_geolocation":   "olist_geolocation_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}

for table_name, filename in tables.items():
    filepath = os.path.join(DATA_DIR, filename)
    print(f"Loading {filename} -> {table_name} ...", end=" ")
    df = pd.read_csv(filepath)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"{len(df)} rows")

print("\nDone! Tables loaded into PostgreSQL:")
for t in tables:
    print(f"  - {t}")
