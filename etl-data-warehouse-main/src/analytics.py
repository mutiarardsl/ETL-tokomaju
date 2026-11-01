import pandas as pd
from tabulate import tabulate
from sqlalchemy.engine import Engine


def print_table(title: str, df: pd.DataFrame, max_rows: int = 10):
    print(f"\n--- {title} ---")
    print(tabulate(df.head(max_rows), headers="keys", tablefmt="simple", showindex=False))


def run_analytics(engine: Engine):
    with engine.connect() as conn:
        q1 = """
        SELECT 
            dp.kategori,
            COUNT(fp.id_penjualan) AS total_transaksi,
            SUM(fp.qty) AS total_unit_terjual,
            SUM(fp.total_penjualan) AS total_pendapatan
        FROM fakta_penjualan fp
        JOIN dim_produk dp ON fp.id_produk = dp.id_produk
        GROUP BY dp.kategori
        ORDER BY total_pendapatan DESC;
        """
        res1 = pd.read_sql(q1, con=conn)
        res1["total_pendapatan"] = res1["total_pendapatan"].apply(lambda x: f"Rp {float(x):,.0f}".replace(",", "."))
        print_table("Penjualan per Kategori Produk", res1)

        q2 = """
        SELECT 
            dpl.kota,
            COUNT(fp.id_penjualan) AS total_transaksi,
            SUM(fp.total_penjualan) AS total_pendapatan
        FROM fakta_penjualan fp
        JOIN dim_pelanggan dpl ON fp.id_pelanggan = dpl.id_pelanggan
        GROUP BY dpl.kota
        ORDER BY total_pendapatan DESC;
        """
        res2 = pd.read_sql(q2, con=conn)
        res2["total_pendapatan"] = res2["total_pendapatan"].apply(lambda x: f"Rp {float(x):,.0f}".replace(",", "."))
        print_table("Penjualan per Kota (Top 5)", res2.head(5))
