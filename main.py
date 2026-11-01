"""CB 2: pipeline ETL lengkap (CB 1 sudah termasuk di dalamnya).

Jalankan:  python main.py
"""
import sys
import time

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pandas as pd

from src.analytics import run_analytics
from src.before_after import tampilkan_before_after
from src.config import DB_SOURCE_NAME, DB_TARGET_NAME
from src.db import (check_server, ensure_database, get_source_engine, get_target_engine,
                    init_source_table, init_target_schema)
from src.extract import extract_customers_db, extract_products_excel, extract_sales_csv
from src.load import (attach_surrogate_keys, load_dimensions,
                      load_fact_and_rejects, reject_frame)
from src.transform import build_star_schema, clean_customers, clean_products, clean_sales
from src.verify import verify


def run_pipeline() -> bool:
    mulai = time.time()
    print("Memulai pipeline ETL TokoMaju...")

    # Persiapan: database sumber dan target, tabel pelanggan, skema star schema
    check_server()
    ensure_database(DB_SOURCE_NAME)
    ensure_database(DB_TARGET_NAME)
    src, dwh = get_source_engine(), get_target_engine()
    init_source_table(src)
    init_target_schema(dwh)

    # 1) EXTRACT
    print("\n[1/5] Extract: membaca 3 sumber data")
    raw_sales = extract_sales_csv()
    raw_products = extract_products_excel()
    raw_customers = extract_customers_db(src)
    print(f"  penjualan.csv : {len(raw_sales)} baris")
    print(f"  produk.xlsx   : {len(raw_products)} baris")
    print(f"  pelanggan (DB): {len(raw_customers)} baris")

    # 2) TRANSFORM
    print("\n[2/5] Transform: cleansing dan membentuk star schema")
    sales = clean_sales(raw_sales)
    products = clean_products(raw_products)
    customers = clean_customers(raw_customers)
    star = build_star_schema(sales.bersih, products, customers)
    st = sales.stat
    print(f"  penjualan : {st['n_mentah']} -> {st['n_bersih']} valid "
          f"(duplikat {st['n_duplikat']}, ditolak {st['n_reject']})")
    print(f"  produk    : {len(raw_products)} -> {len(products)} "
          f"(duplikat {len(raw_products) - len(products)})")
    print(f"  pelanggan : {len(raw_customers)} -> {len(customers)} "
          f"(duplikat {len(raw_customers) - len(customers)})")

    # 3) LOAD dimensi
    print("\n[3/5] Load: dimensi lebih dulu")
    load_dimensions(dwh, star)
    for nama in ("dim_waktu", "dim_produk", "dim_pelanggan"):
        print(f"  {nama}: {len(star[nama])} baris")

    # 4) LOAD fakta (setelah surrogate key dimensi tersedia)
    print("\n[4/5] Load: fakta_penjualan")
    fakta, reject_master = attach_surrogate_keys(dwh, star["fakta_stage"])
    st["n_reject_master"] = len(reject_master)
    st["total_reject_master"] = float(reject_master["total_penjualan"].sum())
    st["reject_master_per_alasan"] = reject_master["alasan"].value_counts().to_dict()
    st["n_fakta"] = len(fakta)
    st["total_fakta"] = float(fakta["total_penjualan"].sum())

    semua_reject = pd.concat([reject_frame(sales.reject), reject_frame(reject_master)], ignore_index=True)
    load_fact_and_rejects(dwh, fakta, semua_reject)
    print(f"  fakta_penjualan  : {len(fakta)} baris")
    print(f"  reject_penjualan : {len(semua_reject)} baris")

    # 5) VERIFIKASI + ANALISIS
    print("\n[5/5] Verifikasi dan query analisis")
    lulus = verify(dwh, st, star)
    run_analytics(dwh)

    print(f"\nSelesai dalam {time.time() - mulai:.1f} detik. "
          f"Bukti tersimpan di folder output/.")

    print()
    tampilkan_before_after(raw_sales, sales, raw_products, products, raw_customers, customers)
    return lulus


if __name__ == "__main__":
    sys.exit(0 if run_pipeline() else 1)
pass

import pandas as pd

from src.analytics import run_analytics
from src.config import DB_SOURCE_NAME, DB_TARGET_NAME
from src.db import (check_server, ensure_database, get_source_engine, get_target_engine,
                    init_source_table, init_target_schema)
from src.extract import extract_customers_db, extract_products_excel, extract_sales_csv
from src.load import (attach_surrogate_keys, load_dimensions,
                      load_fact_and_rejects, reject_frame)
from src.transform import build_star_schema, clean_customers, clean_products, clean_sales
from src.verify import verify


def run_pipeline() -> bool:
    mulai = time.time()
    print("Memulai pipeline ETL TokoMaju...")

    # Persiapan: database sumber dan target, tabel pelanggan, skema star schema
    check_server()
    ensure_database(DB_SOURCE_NAME)
    ensure_database(DB_TARGET_NAME)
    src, dwh = get_source_engine(), get_target_engine()
    init_source_table(src)
    init_target_schema(dwh)

    # 1) EXTRACT
    print("\n[1/5] Extract: membaca 3 sumber data")
    raw_sales = extract_sales_csv()
    raw_products = extract_products_excel()
    raw_customers = extract_customers_db(src)
    print(f"  penjualan.csv : {len(raw_sales)} baris")
    print(f"  produk.xlsx   : {len(raw_products)} baris")
    print(f"  pelanggan (DB): {len(raw_customers)} baris")

    # 2) TRANSFORM
    print("\n[2/5] Transform: cleansing dan membentuk star schema")
    sales = clean_sales(raw_sales)
    products = clean_products(raw_products)
    customers = clean_customers(raw_customers)
    star = build_star_schema(sales.bersih, products, customers)
    st = sales.stat
    print(f"  penjualan : {st['n_mentah']} -> {st['n_bersih']} valid "
          f"(duplikat {st['n_duplikat']}, ditolak {st['n_reject']})")
    print(f"  produk    : {len(raw_products)} -> {len(products)} "
          f"(duplikat {len(raw_products) - len(products)})")
    print(f"  pelanggan : {len(raw_customers)} -> {len(customers)} "
          f"(duplikat {len(raw_customers) - len(customers)})")

    # 3) LOAD dimensi
    print("\n[3/5] Load: dimensi lebih dulu")
    load_dimensions(dwh, star)
    for nama in ("dim_waktu", "dim_produk", "dim_pelanggan"):
        print(f"  {nama}: {len(star[nama])} baris")

    # 4) LOAD fakta (setelah surrogate key dimensi tersedia)
    print("\n[4/5] Load: fakta_penjualan")
    fakta, reject_master = attach_surrogate_keys(dwh, star["fakta_stage"])
    st["n_reject_master"] = len(reject_master)
    st["total_reject_master"] = float(reject_master["total_penjualan"].sum())
    st["reject_master_per_alasan"] = reject_master["alasan"].value_counts().to_dict()
    st["n_fakta"] = len(fakta)
    st["total_fakta"] = float(fakta["total_penjualan"].sum())

    semua_reject = pd.concat([reject_frame(sales.reject), reject_frame(reject_master)], ignore_index=True)
    load_fact_and_rejects(dwh, fakta, semua_reject)
    print(f"  fakta_penjualan  : {len(fakta)} baris")
    print(f"  reject_penjualan : {len(semua_reject)} baris")

    # 5) VERIFIKASI + ANALISIS
    print("\n[5/5] Verifikasi dan query analisis")
    lulus = verify(dwh, st, star)
    run_analytics(dwh)

    print(f"\nSelesai dalam {time.time() - mulai:.1f} detik. "
          f"Bukti tersimpan di folder output/.")
    return lulus


if __name__ == "__main__":
    sys.exit(0 if run_pipeline() else 1)
