import pandas as pd

from src.transform.clean_sales import clean_currency, clean_sales, parse_tanggal


def _sales(rows):
    return pd.DataFrame(rows, columns=[
        "id_transaksi", "tanggal", "id_produk", "id_pelanggan", "qty", "harga_satuan", "metode_bayar"])


def test_tanggal_iso_tidak_tertukar_bulan_hari():
    # Regresi bug: dayfirst=True menukar 2025-11-06 menjadi 11 Juni
    hasil = parse_tanggal(pd.Series(["2025-11-06", "2025-01-02"]))
    assert hasil.dt.strftime("%Y-%m-%d").tolist() == ["2025-11-06", "2025-01-02"]


def test_format_tanggal_lain_dibaca_hari_bulan_tahun():
    hasil = parse_tanggal(pd.Series(["08/12/2025", "08-12-2025", "3 Agu 2025", "13 Mei 2025"]))
    assert hasil.dt.strftime("%Y-%m-%d").tolist() == [
        "2025-12-08", "2025-12-08", "2025-08-03", "2025-05-13"]


def test_harga_rp_dan_kosong():
    assert clean_currency("Rp85.000") == 85000
    assert clean_currency("18000") == 18000
    assert pd.isna(clean_currency(None))


def test_duplikat_reject_dan_total():
    df = _sales([
        ["T1", "2025-01-05", "P1", "C1", "2", "Rp10.000", "QRIS"],
        ["T1", "2025-01-05", "P1", "C1", "2", "Rp10.000", "QRIS"],   # duplikat
        ["T2", "05/01/2025", "P1", "C1", "-1", "10000", "Tunai"],    # qty negatif
        ["T3", "05/01/2025", "P1", None, "1", "10000", "Tunai"],     # pelanggan kosong
        ["T4", "tidak jelas", "P1", "C1", "1", "10000", "Tunai"],    # tanggal rusak
    ])
    hasil = clean_sales(df)
    assert hasil.stat["n_duplikat"] == 1
    assert len(hasil.bersih) == 1
    assert hasil.bersih.iloc[0]["total_penjualan"] == 20000
    assert set(hasil.reject["alasan"]) == {
        "qty negatif atau nol", "id_pelanggan kosong", "tanggal tidak valid"}
    # Rekonsiliasi baris: mentah = duplikat + reject + bersih
    st = hasil.stat
    assert st["n_mentah"] == st["n_duplikat"] + st["n_reject"] + st["n_bersih"]
