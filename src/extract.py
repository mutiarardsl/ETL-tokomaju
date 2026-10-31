import pandas as pd
from sqlalchemy.engine import Engine

from src.config import DATA_RAW_DIR

# Semua kolom CSV/Excel dibaca sebagai teks (dtype=str) agar tidak ada konversi
# diam-diam oleh pandas. Konversi tipe dilakukan sengaja di tahap Transform.


def extract_sales_csv(file_name: str = "penjualan.csv") -> pd.DataFrame:
    file_path = DATA_RAW_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    df = pd.read_csv(file_path, sep=";", dtype=str)
    if len(df.columns) <= 1:  # pemisah ternyata koma
        df = pd.read_csv(file_path, sep=",", dtype=str)
    return df


def extract_products_excel(file_name: str = "produk.xlsx") -> pd.DataFrame:
    file_path = DATA_RAW_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    return pd.read_excel(file_path, sheet_name=0, dtype=str, engine="openpyxl")


def extract_customers_db(engine: Engine, table_name: str = "pelanggan") -> pd.DataFrame:
    # table_name hanya boleh berasal dari kode, bukan input pengguna
    return pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
