import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.db import get_engine, init_source_table, init_target_star_schema
from src.extract import extract_sales_csv, extract_products_excel, extract_customers_db
from src.transform import clean_sales, clean_products, clean_customers, build_star_schema
from src.load import load_star_schema
from src.analytics import run_analytics


def run_pipeline():
    print("Memulai pipeline ETL TokoMaju...")

    engine = get_engine()
    init_source_table(engine)
    init_target_star_schema(engine)

    print("[1/4] Extracting data...")
    raw_sales = extract_sales_csv("penjualan.csv")
    raw_products = extract_products_excel("produk.xlsx")
    raw_customers = extract_customers_db(engine, "pelanggan")

    print("[2/4] Transforming data...")
    cleaned_sales = clean_sales(raw_sales)
    cleaned_products = clean_products(raw_products)
    cleaned_customers = clean_customers(raw_customers)
    star_data = build_star_schema(cleaned_sales, cleaned_products, cleaned_customers)

    print("[3/4] Loading into Star Schema...")
    load_star_schema(star_data, engine, truncate_first=True)

    print("[4/4] Verifikasi hasil pemuatan:")
    for table_name, df in star_data.items():
        print(f"  - {table_name}: {len(df)} baris")

    run_analytics(engine)

    print("\nPipeline ETL selesai dengan sukses.")


if __name__ == "__main__":
    run_pipeline()
