import pandas as pd

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def build_dim_waktu(tgl_min, tgl_maks) -> pd.DataFrame:
    """Kalender lengkap (tanpa celah) dari tanggal pertama sampai terakhir.
    waktu_key = yyyymmdd (surrogate key bertipe angka)."""
    d = pd.Series(pd.date_range(tgl_min, tgl_maks, freq="D"))
    return pd.DataFrame({
        "waktu_key": d.dt.strftime("%Y%m%d").astype(int),
        "tanggal": d.dt.date,
        "hari": d.dt.dayofweek.map(lambda i: HARI[i]),
        "bulan": d.dt.month,
        "nama_bulan": d.dt.month.map(lambda m: BULAN[m - 1]),
        "kuartal": d.dt.quarter,
        "tahun": d.dt.year,
    })


def build_star_schema(
    sales_bersih: pd.DataFrame, df_products: pd.DataFrame, df_customers: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    """Rakit tiga dimensi dan kandidat fakta.

    Kunci surrogate dim_produk dan dim_pelanggan dibuat oleh PostgreSQL saat dimuat,
    sehingga fakta baru bisa diberi kunci setelah dimensi dimuat (lihat load.py)."""
    dim_waktu = build_dim_waktu(sales_bersih["tanggal"].min(), sales_bersih["tanggal"].max())

    fakta_stage = sales_bersih.assign(
        waktu_key=sales_bersih["tanggal"].dt.strftime("%Y%m%d").astype(int)
    )[[
        "id_transaksi", "waktu_key", "id_produk", "id_pelanggan", "metode_bayar",
        "qty", "harga_satuan", "total_penjualan",
        "tanggal_mentah", "qty_mentah", "harga_mentah",
    ]].reset_index(drop=True)

    return {
        "dim_waktu": dim_waktu,
        "dim_produk": df_products,
        "dim_pelanggan": df_customers,
        "fakta_stage": fakta_stage,
    }
