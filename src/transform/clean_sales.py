import re
from typing import NamedTuple

import pandas as pd

BULAN_INDO = {"Mei": "May", "Agu": "Aug", "Agt": "Aug", "Okt": "Oct", "Des": "Dec"}
REGEX_ISO = r"^\d{4}-\d{2}-\d{2}$"


class SalesResult(NamedTuple):
    bersih: pd.DataFrame     # transaksi valid, siap dimuat
    reject: pd.DataFrame     # transaksi ditolak + kolom alasan
    duplikat: pd.DataFrame   # baris duplikat yang dibuang
    stat: dict               # angka untuk rekonsiliasi


def parse_tanggal(s: pd.Series) -> pd.Series:
    """Seragamkan format tanggal campur.

    - ISO (2025-11-06) dibaca eksplisit sebagai tahun-bulan-hari. Tidak boleh memakai
      dayfirst, karena dayfirst=True ikut menukar bulan dan hari pada tanggal ISO.
    - Format lain (08/12/2025, 08-12-2025, 3 Agu 2025) dibaca hari-bulan-tahun.
    """
    s = s.astype("object").map(lambda v: None if pd.isna(v) else str(v).strip())
    for id_m, en_m in BULAN_INDO.items():
        s = s.map(lambda v, a=id_m, b=en_m: v if v is None else re.sub(rf"\b{a}\b", b, v))
    s = pd.Series(s, dtype="object")

    is_iso = s.map(lambda v: bool(v) and re.match(REGEX_ISO, v) is not None)
    iso = pd.to_datetime(s.where(is_iso), format="%Y-%m-%d", errors="coerce")
    lain = pd.to_datetime(s.where(~is_iso), format="mixed", dayfirst=True, errors="coerce")
    return iso.fillna(lain)


def clean_currency(val):
    """'Rp85.000' -> 85000.0 ; kosong -> NaN (jangan diam-diam menjadi 0)."""
    if val is None or pd.isna(val):
        return float("nan")
    digits = re.sub(r"[^\d]", "", str(val))
    return float(digits) if digits else float("nan")


def _bersihkan_teks(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        out[c] = out[c].map(lambda v: None if pd.isna(v) else (str(v).strip() or None))
    return out


def clean_sales(df_raw: pd.DataFrame) -> SalesResult:
    s = _bersihkan_teks(df_raw)
    if "id_transaksi" not in s.columns and "id" in s.columns:
        s = s.rename(columns={"id": "id_transaksi"})

    w = pd.DataFrame({
        "id_transaksi": s["id_transaksi"],
        "tanggal_mentah": s["tanggal"],
        "tanggal": parse_tanggal(s["tanggal"]),
        "id_produk": s["id_produk"],
        "id_pelanggan": s["id_pelanggan"],
        "qty_mentah": s["qty"],
        "harga_mentah": s["harga_satuan"],
        "qty": pd.to_numeric(s["qty"], errors="coerce"),
        "harga_satuan": s["harga_satuan"].map(clean_currency),
        "metode_bayar": s["metode_bayar"] if "metode_bayar" in s.columns else None,
    })
    w["nilai"] = (w["qty"] * w["harga_satuan"]).fillna(0)   # dasar rekonsiliasi nilai

    stat = {"n_mentah": len(w), "total_mentah": float(w["nilai"].sum())}

    # 1) Hapus duplikat berdasarkan id_transaksi (kemunculan pertama dipertahankan)
    dup_mask = w.duplicated(subset="id_transaksi", keep="first")
    duplikat = w[dup_mask]
    w = w[~dup_mask].copy()
    stat["n_duplikat"] = int(dup_mask.sum())
    stat["total_duplikat"] = float(duplikat["nilai"].sum())

    # 2) Tandai baris bermasalah (alasan pertama yang cocok yang dipakai)
    alasan = pd.Series([None] * len(w), index=w.index, dtype="object")

    def tandai(mask, teks):
        alasan[mask & alasan.isna()] = teks

    tandai(w["tanggal"].isna(), "tanggal tidak valid")
    tandai(w["id_produk"].isna(), "id_produk kosong")
    tandai(w["id_pelanggan"].isna(), "id_pelanggan kosong")
    tandai(w["qty"].isna(), "qty kosong")
    tandai(w["qty"] <= 0, "qty negatif atau nol")
    tandai(w["harga_satuan"].isna(), "harga kosong")

    reject = w[alasan.notna()].assign(alasan=alasan[alasan.notna()])
    bersih = w[alasan.isna()].copy()
    stat["n_reject"] = len(reject)
    stat["total_reject"] = float(reject["nilai"].sum())
    stat["reject_per_alasan"] = reject["alasan"].value_counts().to_dict()

    # 3) Kolom turunan
    bersih["qty"] = bersih["qty"].astype(int)
    bersih["total_penjualan"] = (bersih["qty"] * bersih["harga_satuan"]).round(2)
    stat["n_bersih"] = len(bersih)
    stat["total_bersih"] = float(bersih["total_penjualan"].sum())

    return SalesResult(bersih.drop(columns="nilai"), reject.drop(columns="nilai"), duplikat, stat)
