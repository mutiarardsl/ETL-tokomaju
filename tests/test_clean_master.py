import pandas as pd

from src.transform.clean_customers import (clean_customers, standardize_city,
                                           standardize_gender, standardize_phone)
from src.transform.clean_products import clean_products, standardize_category


def test_kategori_diseragamkan():
    for v in ["Elektronik", "elektronik ", "ELEKTRONIK"]:
        assert standardize_category(v) == "Elektronik"
    assert standardize_category(None) == "Tidak Diketahui"


def test_produk_duplikat_dihapus():
    df = pd.DataFrame({"id_produk": ["P1", "P1", " P2"], "nama_produk": ["A", "A", "B"],
                       "kategori": ["Fashion", "Fashion", "mamin"]})
    out = clean_products(df)
    assert out["id_produk"].tolist() == ["P1", "P2"]
    assert out["kategori"].tolist() == ["Fashion", "Makanan & Minuman"]


def test_kota_dan_telepon():
    assert standardize_city("Mlg") == "Malang"
    assert standardize_city("") == "Tidak Diketahui"
    assert standardize_city(None) == "Tidak Diketahui"
    for v in ["+6281283822264", "081283822264", "(0812) 8382-2264", "6281283822264"]:
        assert standardize_phone(v) == "081283822264"
    assert standardize_phone(None) is None


def test_gender_diseragamkan():
    for v in ["L", "l", "Laki-laki", "Pria"]:
        assert standardize_gender(v) == "Laki-laki"
    for v in ["P", "p", "Perempuan", "Wanita"]:
        assert standardize_gender(v) == "Perempuan"
    assert standardize_gender(None) == "Tidak Diketahui"
    assert standardize_gender("lainnya") == "Tidak Diketahui"


def test_clean_customers_menerapkan_semua_aturan():
    df = pd.DataFrame({
        "id_pelanggan": ["C1", "C2"], "nama": ["A", "B"], "jenis_kelamin": ["Wanita", "l"],
        "kota": [None, "Mlg"], "telepon": ["+6281283822264", None],
    })
    out = clean_customers(df)
    assert out["jenis_kelamin"].tolist() == ["Perempuan", "Laki-laki"]
    assert out["kota"].tolist() == ["Tidak Diketahui", "Malang"]      # tidak boleh ada kota NULL
    assert out["telepon"].iloc[0] == "081283822264"
    assert out["telepon"].isna().tolist() == [False, True]            # kosong menjadi NULL


def test_metode_bayar_diseragamkan_dan_dimensi_dibentuk():
    from src.transform.build_star_schema import build_star_schema
    from src.transform.clean_sales import standardize_payment
    assert standardize_payment(" qris ") == "QRIS"
    assert standardize_payment("TUNAI") == "Tunai"
    assert standardize_payment(None) == "Tidak Diketahui"

    sales = pd.DataFrame({
        "id_transaksi": ["T1", "T2", "T3"],
        "tanggal": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-02"]),
        "id_produk": ["P1"] * 3, "id_pelanggan": ["C1"] * 3,
        "metode_bayar": ["Tunai", "QRIS", "Tunai"],
        "qty": [1, 1, 1], "harga_satuan": [1.0] * 3, "total_penjualan": [1.0] * 3,
        "tanggal_mentah": ["a"] * 3, "qty_mentah": ["1"] * 3, "harga_mentah": ["1"] * 3,
    })
    star = build_star_schema(sales, pd.DataFrame(), pd.DataFrame())
    assert star["dim_metode_bayar"]["metode_bayar"].tolist() == ["QRIS", "Tunai"]   # unik dan terurut
