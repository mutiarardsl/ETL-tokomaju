import pandas as pd


def build_star_schema(
    df_sales: pd.DataFrame, df_products: pd.DataFrame, df_customers: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    unique_dates = pd.to_datetime(pd.Series(df_sales["tanggal"].unique())).sort_values()
    hari_indo = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }
    dim_waktu = pd.DataFrame({
        "tanggal": unique_dates.dt.date,
        "hari": unique_dates.dt.day_name().map(hari_indo).fillna(unique_dates.dt.day_name()),
        "bulan": unique_dates.dt.month,
        "kuartal": unique_dates.dt.quarter,
        "tahun": unique_dates.dt.year,
    })

    dim_produk = df_products.copy()
    dim_pelanggan = df_customers.copy()

    fakta_penjualan = df_sales.rename(columns={"id_transaksi": "id_penjualan"})[
        ["id_penjualan", "tanggal", "id_produk", "id_pelanggan", "qty", "total_penjualan", "metode_bayar"]
    ].copy()

    valid_products = set(dim_produk["id_produk"])
    valid_customers = set(dim_pelanggan["id_pelanggan"])
    valid_dates = set(dim_waktu["tanggal"])

    fakta_penjualan = fakta_penjualan[
        fakta_penjualan["id_produk"].isin(valid_products)
        & fakta_penjualan["id_pelanggan"].isin(valid_customers)
        & fakta_penjualan["tanggal"].isin(valid_dates)
    ]

    return {
        "dim_waktu": dim_waktu,
        "dim_produk": dim_produk,
        "dim_pelanggan": dim_pelanggan,
        "fakta_penjualan": fakta_penjualan,
    }
