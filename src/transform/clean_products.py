import re

import pandas as pd


def standardize_category(cat) -> str:
    if pd.isna(cat) or not str(cat).strip():
        return "Tidak Diketahui"
    c = re.sub(r"\s+", " ", str(cat)).strip().lower()
    if "mamin" in c or "makanan" in c:
        return "Makanan & Minuman"
    if "rumah" in c:
        return "Rumah Tangga"
    if "fashion" in c:
        return "Fashion"
    if "kesehatan" in c or "kecantikan" in c:
        return "Kesehatan & Kecantikan"
    if "elektronik" in c:
        return "Elektronik"
    if "olahraga" in c:
        return "Olahraga"
    return c.title()


def clean_products(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()
    df["id_produk"] = df["id_produk"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["id_produk"], keep="first")

    name_col = "nama_produk" if "nama_produk" in df.columns else "produk"
    df["produk"] = df[name_col].astype(str).str.strip()
    df["kategori"] = df["kategori"].map(standardize_category)
    return df[["id_produk", "produk", "kategori"]].reset_index(drop=True)
