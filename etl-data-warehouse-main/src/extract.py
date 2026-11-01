import pandas as pd
from sqlalchemy.engine import Engine
from src.config import DATA_RAW_DIR


def extract_sales_csv(file_name: str = "penjualan.csv") -> pd.DataFrame:
    file_path = DATA_RAW_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_csv(file_path, sep=";")
        if len(df.columns) <= 1:
            df = pd.read_csv(file_path, sep=",")
    except Exception:
        df = pd.read_csv(file_path, sep=",")

    return df


def extract_products_excel(file_name: str = "produk.xlsx") -> pd.DataFrame:
    file_path = DATA_RAW_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return pd.read_excel(file_path, sheet_name=0)


def extract_customers_db(engine: Engine, table_name: str = "pelanggan") -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
