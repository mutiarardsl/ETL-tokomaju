import re
import pandas as pd


def clean_sales(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()
    id_col = "id_transaksi" if "id_transaksi" in df.columns else "id"

    df = df.drop_duplicates(subset=[id_col], keep="first")

    indo_months = {
        "Jan": "Jan", "Feb": "Feb", "Mar": "Mar", "Apr": "Apr",
        "Mei": "May", "Jun": "Jun", "Jul": "Jul", "Agu": "Aug", "Agt": "Aug",
        "Sep": "Sep", "Okt": "Oct", "Nov": "Nov", "Des": "Dec"
    }
    date_series = df["tanggal"].astype(str)
    for id_m, en_m in indo_months.items():
        date_series = date_series.str.replace(rf"\b{id_m}\b", en_m, regex=True)

    parsed_dates = pd.to_datetime(date_series, format="mixed", dayfirst=True, errors="coerce")
    df = df[parsed_dates.notna()].copy()
    df["tanggal"] = parsed_dates[parsed_dates.notna()].dt.date

    def clean_currency(val):
        if pd.isna(val):
            return 0.0
        val_str = re.sub(r"[^\d]", "", str(val))
        return float(val_str) if val_str else 0.0

    df["harga_satuan"] = df["harga_satuan"].apply(clean_currency)
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(0).astype(int)
    df = df[df["qty"] > 0].copy()

    df["total_penjualan"] = df["qty"] * df["harga_satuan"]
    df["id_transaksi"] = df[id_col].astype(str).str.strip()
    df["id_produk"] = df["id_produk"].astype(str).str.strip()
    df["id_pelanggan"] = df["id_pelanggan"].astype(str).str.strip()

    if "metode_bayar" in df.columns:
        df["metode_bayar"] = df["metode_bayar"].astype(str).str.strip()

    return df
