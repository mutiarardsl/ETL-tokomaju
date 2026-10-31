import pandas as pd
from tabulate import tabulate

from src.report import Report


def profile_source(rep: Report, nama: str, jenis: str, df: pd.DataFrame) -> None:
    rep.add(f"\n--- {nama} ({jenis}) ---")
    rep.add(f"Jumlah baris : {len(df)}")
    rep.add(f"Jumlah kolom : {len(df.columns)} -> {', '.join(map(str, df.columns))}")
    # Kosong = NULL/NaN ATAU teks kosong (isna() saja tidak menghitung string kosong)
    kosong = df.apply(lambda c: c.map(lambda v: bool(pd.isna(v)) or (isinstance(v, str) and not v.strip())).sum())
    kosong = kosong[kosong > 0]
    rep.add("Nilai kosong : " + (", ".join(f"{k}={v}" for k, v in kosong.items()) or "tidak ada"))
    rep.add("Contoh 3 baris pertama:")
    rep.add(tabulate(df.head(3), headers="keys", tablefmt="simple", showindex=False))


def dedup_report(rep: Report, nama: str, df: pd.DataFrame, key: str):
    """Hapus duplikat berdasarkan kolom kunci; tampilkan bukti sebelum dan sesudah."""
    sebelum = len(df)
    bersih = df.drop_duplicates(subset=[key], keep="first")
    sesudah = len(bersih)
    rep.add(f"\n[{nama}] kunci duplikat: {key}")
    rep.add(f"  Sebelum : {sebelum} baris")
    rep.add(f"  Sesudah : {sesudah} baris")
    rep.add(f"  Dibuang : {sebelum - sesudah} baris duplikat")
    if sebelum != sesudah:
        contoh = df[df.duplicated(subset=[key], keep=False)].sort_values(key).head(4)
        rep.add("  Contoh baris duplikat:")
        rep.add(tabulate(contoh, headers="keys", tablefmt="simple", showindex=False))
    return bersih
