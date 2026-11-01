import pandas as pd
from src.config import DATA_RAW_DIR

raw = pd.read_csv(DATA_RAW_DIR / 'penjualan.csv', sep=';', dtype=str)

print(raw.shape)                                          # (2445, 7)
print(raw.duplicated(subset='id_transaksi').sum())        # 45 duplikat
print(raw.isna().sum()[lambda s: s > 0])                  # id_pelanggan = 27
print((pd.to_numeric(raw['qty']) <= 0).sum())             # 25 (24 setelah duplikat dibuang)

# Pola tanggal: angka diganti 9, huruf diganti A
pola = (raw['tanggal'].str.replace(r'\d', '9', regex=True)
                      .str.replace(r'[A-Za-z]+', 'A', regex=True))
print(pola.value_counts())     # 9999-99-99: 1388 | 99/99/9999: 588 | 99-99-9999: 275 | 99 A 9999: 141 | 9 A 9999: 53

# Pola harga
print(raw['harga_satuan'].str.replace(r'\d', '9', regex=True).value_counts())   # ada 'Rp99.999'

# Satu transaksi di CSV
print(raw[raw.id_transaksi == 'T00003'])    # tanggal 2025-11-06