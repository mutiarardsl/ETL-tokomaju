import pandas as pd

from src.transform.clean_customers import standardize_city, standardize_phone
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
