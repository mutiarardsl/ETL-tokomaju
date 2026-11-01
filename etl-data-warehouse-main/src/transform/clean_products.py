import pandas as pd


def clean_products(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()
    df = df.drop_duplicates(subset=["id_produk"], keep="first")

    if "nama_produk" in df.columns:
        df["produk"] = df["nama_produk"].astype(str).str.strip()
    elif "produk" in df.columns:
        df["produk"] = df["produk"].astype(str).str.strip()

    df["id_produk"] = df["id_produk"].astype(str).str.strip()
    df["kategori"] = df["kategori"].fillna("Kesehatan & Kecantikan")

    def standardize_category(cat: str) -> str:
        c = str(cat).strip().lower()
        if "mamin" in c or "makanan" in c:
            return "Makanan & Minuman"
        elif "rumah" in c:
            return "Rumah Tangga"
        elif "fashion" in c:
            return "Fashion"
        elif "kesehatan" in c or "kecantikan" in c:
            return "Kesehatan & Kecantikan"
        elif "elektronik" in c:
            return "Elektronik"
        elif "olahraga" in c:
            return "Olahraga"
        return str(cat).strip().title()

    df["kategori"] = df["kategori"].apply(standardize_category)
    return df[["id_produk", "produk", "kategori"]]
