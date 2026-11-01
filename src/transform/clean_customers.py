import re

import pandas as pd

CITY_MAPPING = {
    "mlg": "Malang", "malang": "Malang", "kota malang": "Malang",
    "batu": "Batu", "kota batu": "Batu",
    "sby": "Surabaya", "surabaya": "Surabaya", "kota surabaya": "Surabaya",
    "sda": "Sidoarjo", "sidoarjo": "Sidoarjo",
    "dki jakarta": "Jakarta", "jakarta": "Jakarta",
    "bandung": "Bandung", "denpasar": "Denpasar", "semarang": "Semarang",
    "kediri": "Kediri", "pasuruan": "Pasuruan", "blitar": "Blitar",
    "yogyakarta": "Yogyakarta",
}

GENDER_MAPPING = {
    "l": "Laki-laki", "laki-laki": "Laki-laki", "pria": "Laki-laki",
    "p": "Perempuan", "perempuan": "Perempuan", "wanita": "Perempuan",
}


def standardize_gender(val) -> str:
    if pd.isna(val):
        return "Tidak Diketahui"
    return GENDER_MAPPING.get(str(val).strip().lower(), "Tidak Diketahui")


def standardize_city(val) -> str:
    if pd.isna(val):
        return "Tidak Diketahui"
    c = str(val).strip()
    if c.lower() in ("", "null", "none", "nan", "-"):
        return "Tidak Diketahui"
    return CITY_MAPPING.get(c.lower(), c.title())


def standardize_phone(val):
    """Semua format -> 08xxxxxxxxxx. Kosong -> None (NULL di database)."""
    if pd.isna(val):
        return None
    digits = re.sub(r"\D", "", str(val))
    if not digits:
        return None
    if digits.startswith("62"):
        digits = "0" + digits[2:]
    elif digits.startswith("8"):
        digits = "0" + digits
    return digits


def clean_customers(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()
    df["id_pelanggan"] = df["id_pelanggan"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["id_pelanggan"], keep="first")

    name_col = "nama" if "nama" in df.columns else "pelanggan"
    df["pelanggan"] = df[name_col].astype(str).str.strip()
    df["jenis_kelamin"] = df["jenis_kelamin"].map(standardize_gender)
    df["kota"] = df["kota"].map(standardize_city)
    df["telepon"] = df["telepon"].map(standardize_phone) if "telepon" in df.columns else None
    return df[["id_pelanggan", "pelanggan", "jenis_kelamin", "kota", "telepon"]].reset_index(drop=True)