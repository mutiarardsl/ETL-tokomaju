import re

import pandas as pd
from sqlalchemy.engine import Engine
from tabulate import tabulate

from src.config import OUTPUT_DIR, SQL_DIR

BULAN_SINGKAT = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def rupiah(x) -> str:
    return f"Rp {float(x):,.0f}".replace(",", ".")


def load_queries() -> dict[str, str]:
    """Baca sql/02_query_analisis.sql; tiap query diawali baris '-- name: nama_query'."""
    isi = (SQL_DIR / "02_query_analisis.sql").read_text(encoding="utf-8")
    bagian = re.split(r"^-- name:\s*(\w+)\s*$", isi, flags=re.MULTILINE)
    return {bagian[i]: bagian[i + 1].strip() for i in range(1, len(bagian), 2)}


def run_analytics(engine: Engine) -> None:
    queries = load_queries()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Query utama CB 2: total penjualan per kategori per bulan
    df = pd.read_sql(queries["kategori_per_bulan"], engine)
    df.to_csv(OUTPUT_DIR / "analisis_kategori_per_bulan.csv", index=False)
    pivot = (df.pivot_table(index="kategori", columns="bulan", values="total_penjualan",
                            aggfunc="sum", fill_value=0) / 1_000_000)
    pivot.columns = [BULAN_SINGKAT[int(b) - 1] for b in pivot.columns]
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("Total", ascending=False)
    print("\n--- Total penjualan per kategori per bulan (juta Rp) ---")
    print(tabulate(pivot.reset_index(), headers="keys", tablefmt="simple",
                   floatfmt=".1f", showindex=False))

    # 2) Ringkasan per kategori
    k = pd.read_sql(queries["total_per_kategori"], engine)
    k["total_penjualan"] = k["total_penjualan"].map(rupiah)
    print("\n--- Total penjualan per kategori ---")
    print(tabulate(k, headers="keys", tablefmt="simple", showindex=False))

    # 3) Top 5 kota
    c = pd.read_sql(queries["total_per_kota"], engine).head(5)
    c["total_penjualan"] = c["total_penjualan"].map(rupiah)
    print("\n--- Top 5 kota ---")
    print(tabulate(c, headers="keys", tablefmt="simple", showindex=False))
