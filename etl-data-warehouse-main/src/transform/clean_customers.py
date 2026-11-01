import re
import pandas as pd


def clean_customers(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()
    df = df.drop_duplicates(subset=["id_pelanggan"], keep="first")

    name_col = "nama" if "nama" in df.columns else "pelanggan"
    df["pelanggan"] = df[name_col].astype(str).str.strip()
    df["id_pelanggan"] = df["id_pelanggan"].astype(str).str.strip()

    city_mapping = {
        "mlg": "Malang", "malang": "Malang", "kota malang": "Malang",
        "batu": "Batu", "kota batu": "Batu",
        "sby": "Surabaya", "surabaya": "Surabaya", "kota surabaya": "Surabaya",
        "sda": "Sidoarjo", "sidoarjo": "Sidoarjo",
        "dki jakarta": "Jakarta", "jakarta": "Jakarta",
        "bandung": "Bandung", "denpasar": "Denpasar", "semarang": "Semarang",
        "kediri": "Kediri", "pasuruan": "Pasuruan", "blitar": "Blitar", "yogyakarta": "Yogyakarta",
    }

    def standardize_city(city_val):
        if pd.isna(city_val):
            return "Tidak Diketahui"
        c = str(city_val).strip()
        if not c or c.lower() in ["null", "none", "nan", "-", ""]:
            return "Tidak Diketahui"
        return city_mapping.get(c.lower(), c.title())

    df["kota"] = df["kota"].apply(standardize_city)

    def standardize_phone(val):
        if pd.isna(val):
            return "Tidak Ada"
        digits = re.sub(r"\D", "", str(val))
        if digits.startswith("628"):
            digits = "08" + digits[3:]
        elif digits.startswith("8"):
            digits = "0" + digits
        return digits if digits else "Tidak Ada"

    if "telepon" in df.columns:
        df["telepon"] = df["telepon"].apply(standardize_phone)

    return df[["id_pelanggan", "pelanggan", "kota"]]
