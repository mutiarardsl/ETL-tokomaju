"""CB 1: koneksi ke 3 sumber data (CSV, Excel, database) + hapus baris duplikat.

Jalankan:  python run_cb1.py
Bukti tersimpan di output/cb1_extract_report.txt
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sqlalchemy import text

from src.config import DB_SOURCE_NAME, DB_TARGET_NAME, OUTPUT_DIR
from src.db import (check_server, ensure_database, get_source_engine, get_target_engine,
                    init_source_table)
from src.extract import extract_customers_db, extract_products_excel, extract_sales_csv
from src.profiling import dedup_report, profile_source
from src.report import Report


def main():
    rep = Report()
    rep.add("CB 1: EXTRACT 3 SUMBER + HAPUS DUPLIKAT")
    rep.add("=" * 70)

    # Koneksi database sumber dan target
    check_server()
    for nama in (DB_SOURCE_NAME, DB_TARGET_NAME):
        baru = ensure_database(nama)
        rep.add(f"Database {nama}: {'dibuat' if baru else 'sudah ada'}")
    src, dwh = get_source_engine(), get_target_engine()
    dimuat = init_source_table(src)
    rep.add(f"Tabel pelanggan di {DB_SOURCE_NAME}: {'dimuat dari pelanggan.sql' if dimuat else 'sudah berisi data'}")
    for nama, eng in ((DB_SOURCE_NAME, src), (DB_TARGET_NAME, dwh)):
        with eng.connect() as conn:
            versi = conn.execute(text("SELECT version()")).scalar().split(",")[0]
        rep.add(f"Koneksi {nama}: OK ({versi})")

    # Extract
    rep.add("\n" + "=" * 70)
    rep.add("EXTRACT")
    rep.add("=" * 70)
    penjualan = extract_sales_csv()
    produk = extract_products_excel()
    pelanggan = extract_customers_db(src)
    profile_source(rep, "penjualan.csv", "CSV", penjualan)
    profile_source(rep, "produk.xlsx", "Excel", produk)
    profile_source(rep, "pelanggan", "tabel PostgreSQL", pelanggan)

    # Transform CB 1: hapus baris duplikat
    rep.add("\n" + "=" * 70)
    rep.add("TRANSFORM CB 1: HAPUS BARIS DUPLIKAT")
    rep.add("=" * 70)
    dedup_report(rep, "penjualan", penjualan, "id_transaksi")
    dedup_report(rep, "produk", produk, "id_produk")
    dedup_report(rep, "pelanggan", pelanggan, "id_pelanggan")

    path = rep.save(OUTPUT_DIR / "cb1_extract_report.txt")
    print(f"\nLaporan tersimpan di: {path}")


if __name__ == "__main__":
    main()
