from extract import extract_penjualan, extract_produk, extract_pelanggan

# 1) Extract tiga sumber
raw_p = extract_penjualan()    # CSV
raw_pr = extract_produk()      # Excel
raw_pl = extract_pelanggan()   # tabel database

for nama, df in [('penjualan (CSV)', raw_p),
                 ('produk (Excel)', raw_pr),
                 ('pelanggan (DB)', raw_pl)]:
    print(nama, '-> baris:', len(df), '| kolom:', list(df.columns))

# 2) Hapus duplikat pada penjualan
raw = raw_p.copy()
for c in raw.columns:
    raw[c] = raw[c].str.strip()          # rapikan spasi dulu

# Hapus duplikat pada produk
pr = raw_pr.copy()
for c in pr.columns:
    pr[c] = pr[c].str.strip()  

bersih = raw.drop_duplicates()
print('Sebelum:', len(raw_p))
print('Sesudah:', len(bersih))

pr_bersih = pr.drop_duplicates()
print('Produk sebelum:', len(raw_pr))
print('Produk sesudah:', len(pr_bersih))
print('Duplikat produk dihapus:', len(raw_pr) - len(pr_bersih))

# 3) Bukti untuk laporan: contoh baris duplikat
print(raw[raw.duplicated(keep=False)].sort_values('id_transaksi').head(10))
print(pr[pr.duplicated(keep=False)].sort_values('id_produk'))

# 4) Cek apakah masih ada id ganda dengan isi berbeda
print('id_transaksi ganda tersisa:', bersih['id_transaksi'].duplicated().sum())
print('id_produk ganda tersisa:', pr_bersih['id_produk'].duplicated().sum())