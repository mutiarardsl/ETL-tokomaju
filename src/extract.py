import pandas as pd
from db import src_engine

def extract_penjualan(path='data/penjualan.csv'):
    return pd.read_csv(path, sep=';', dtype=str)

def extract_produk(path='data/produk.xlsx'):
    return pd.read_excel(path, dtype=str, engine='openpyxl')

def extract_pelanggan():
    return pd.read_sql('SELECT * FROM pelanggan', src_engine)

if __name__ == '__main__':
    for nama, fn in [('CSV penjualan', extract_penjualan),
                     ('Excel produk', extract_produk),
                     ('DB pelanggan', extract_pelanggan)]:
        df = fn()
        print(f'--- {nama}: {df.shape[0]} baris, {df.shape[1]} kolom')
        print(df.head())