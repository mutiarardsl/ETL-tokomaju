import pandas as pd
from sqlalchemy.engine import Engine

DIM_ORDER = ["dim_waktu", "dim_produk", "dim_pelanggan"]

KOLOM_FAKTA = [
    "id_transaksi", "waktu_key", "produk_key", "pelanggan_key",
    "metode_bayar", "qty", "harga_satuan", "total_penjualan",
]
KOLOM_REJECT = [
    "id_transaksi", "tanggal_mentah", "id_produk", "id_pelanggan",
    "qty", "harga_satuan", "alasan",
]


def load_dimensions(engine: Engine, star: dict[str, pd.DataFrame]) -> None:
    """Langkah 1: muat semua dimensi (kunci surrogate dibuat oleh PostgreSQL)."""
    with engine.begin() as conn:  # satu transaksi: gagal berarti rollback semua
        for name in DIM_ORDER:
            star[name].to_sql(name, conn, if_exists="append", index=False)


def attach_surrogate_keys(engine: Engine, fakta_stage: pd.DataFrame):
    """Langkah 2: ambil surrogate key dari dimensi yang sudah dimuat, lalu petakan ke fakta.
    Transaksi yang produk/pelanggannya tidak ada di master dipisahkan ke reject."""
    dp = pd.read_sql("SELECT produk_key, id_produk FROM dim_produk", engine)
    dc = pd.read_sql("SELECT pelanggan_key, id_pelanggan FROM dim_pelanggan", engine)

    f = (fakta_stage
         .merge(dp, on="id_produk", how="left")
         .merge(dc, on="id_pelanggan", how="left"))

    f["alasan"] = None
    f.loc[f["produk_key"].isna(), "alasan"] = "id_produk tidak ada di master"
    f.loc[f["alasan"].isna() & f["pelanggan_key"].isna(), "alasan"] = "id_pelanggan tidak ada di master"

    reject = f[f["alasan"].notna()].copy()

    fakta = f[f["alasan"].isna()].copy()
    fakta["produk_key"] = fakta["produk_key"].astype(int)
    fakta["pelanggan_key"] = fakta["pelanggan_key"].astype(int)
    return fakta[KOLOM_FAKTA], reject


def reject_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Samakan kolom reject dari tahap clean_sales dan dari tahap lookup kunci."""
    out = df.copy()
    if "qty_mentah" in out.columns:
        out["qty"] = out["qty_mentah"]
    if "harga_mentah" in out.columns:
        out["harga_satuan"] = out["harga_mentah"]
    return out[KOLOM_REJECT].astype(object).where(out[KOLOM_REJECT].notna(), None)


def load_fact_and_rejects(engine: Engine, fakta: pd.DataFrame, rejects: pd.DataFrame) -> None:
    """Langkah 3: muat fakta dan log reject dalam satu transaksi."""
    with engine.begin() as conn:
        fakta.to_sql("fakta_penjualan", conn, if_exists="append", index=False)
        if len(rejects):
            rejects.to_sql("reject_penjualan", conn, if_exists="append", index=False)
