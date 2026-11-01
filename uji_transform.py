import pandas as pd
from src.transform.clean_sales import parse_tanggal, clean_currency, clean_sales
from src.transform.clean_products import standardize_category
from src.transform.clean_customers import standardize_city, standardize_phone

parse_tanggal(pd.Series(['2025-11-06', '08/12/2025', '3 Agu 2025']))
# -> 2025-11-06, 2025-12-08, 2025-08-03

clean_currency('Rp85.000')            # 85000.0
clean_currency(None)                  # nan (bukan 0)
standardize_category('MAMIN')         # 'Makanan & Minuman'
standardize_city('Mlg')               # 'Malang'
standardize_phone('+6281283822264')   # '081283822264'

hasil = clean_sales(df_raw)
hasil.stat                            # n_mentah 2445, n_duplikat 45, n_reject 49, n_bersih 2351
hasil.reject['alasan'].value_counts() # id_pelanggan kosong 25, qty negatif atau nol 24
hasil.duplikat.head()                 # baris duplikat yang dibuang