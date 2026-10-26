from extract import extract_penjualan, extract_produk, extract_pelanggan

raw_p, raw_pr, raw_pl = extract_penjualan(), extract_produk(), extract_pelanggan()

for nama, df in [('penjualan', raw_p), ('produk', raw_pr), ('pelanggan', raw_pl)]:
    print(f'\n===== {nama} {df.shape} =====')
    print(df.isna().sum())
    print('baris duplikat penuh:', df.duplicated().sum())

print(raw_p['tanggal'].sample(20, random_state=1))
print(raw_pr['kategori'].value_counts(dropna=False))
print(raw_pl['kota'].isna().sum(), raw_pl['telepon'].head(15))