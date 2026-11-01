import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def load_star_schema(star_data: dict[str, pd.DataFrame], engine: Engine, truncate_first: bool = True):
    load_order = ["dim_waktu", "dim_produk", "dim_pelanggan", "fakta_penjualan"]

    with engine.begin() as conn:
        if truncate_first:
            for table_name in reversed(load_order):
                conn.execute(text(f"DELETE FROM {table_name}"))

    for table_name in load_order:
        df = star_data[table_name]
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
