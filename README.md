# ETL TokoMaju: Python (pandas + SQLAlchemy) + PostgreSQL

Pipeline ETL untuk Tugas 1 (CB 1) dan Tugas 2 (CB 2) mata kuliah Data Warehouse.
CB 2 sudah mencakup CB 1.

## Arsitektur singkat

```
penjualan.csv  --+
produk.xlsx    --+--> pandas DataFrame --> cleansing --> star schema --> PostgreSQL tokomaju_dwh
pelanggan (DB) --+        (Extract)        (Transform)                   (Load, lewat SQLAlchemy + psycopg2)
 tokomaju_oltp
```

| Database | Fungsi |
| --- | --- |
| `tokomaju_oltp` | Sumber: tabel `pelanggan` (dimuat dari `data/raw/pelanggan.sql`) |
| `tokomaju_dwh` | Target: `dim_waktu`, `dim_produk`, `dim_pelanggan`, `fakta_penjualan`, `reject_penjualan` |

## Menjalankan

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # Linux/macOS: cp .env.example .env  (lalu sesuaikan DB_PASSWORD)

python run_cb1.py                 # CB 1: extract 3 sumber + hapus duplikat
python main.py                    # CB 2: pipeline lengkap + verifikasi + analisis
python -m pytest -q               # (opsional) unit test transformasi
```

PostgreSQL bisa dari instalasi lokal atau `docker compose up -d`.
Kedua database dibuat otomatis oleh pipeline bila belum ada.

## Struktur

| File | Fungsi |
| --- | --- |
| `run_cb1.py` | Mode CB 1, menyimpan bukti ke `output/cb1_extract_report.txt` |
| `main.py` | Mode CB 2, urutan Extract, Transform, Load dimensi, Load fakta, Verifikasi |
| `sql/00_drop_tables.sql`, `sql/01_create_tables.sql` | DDL star schema (dijalankan oleh pipeline) |
| `sql/02_query_analisis.sql` | Query analisis (total per kategori per bulan, dll.) |
| `src/extract.py` | Membaca CSV, Excel, dan tabel database |
| `src/transform/` | `clean_sales`, `clean_products`, `clean_customers`, `build_star_schema` |
| `src/load.py` | Memuat dimensi, memetakan surrogate key, memuat fakta dan reject |
| `src/verify.py` | Rekonsiliasi baris dan nilai, pemeriksaan integritas, simpan `output/verifikasi.txt` |
| `src/analytics.py` | Menjalankan query analisis, simpan `output/analisis_kategori_per_bulan.csv` |
| `tests/` | Unit test untuk tanggal, duplikat, reject, kategori, kota, telepon |

## Keputusan desain

- Surrogate key: `dim_waktu.waktu_key` (yyyymmdd), `dim_produk.produk_key` dan `dim_pelanggan.pelanggan_key` (IDENTITY). `id_produk` dan `id_pelanggan` tetap disimpan sebagai business key.
- Tanggal berformat ISO dibaca eksplisit tahun-bulan-hari. Format lain dibaca hari-bulan-tahun (asumsi).
- Baris yang tidak lolos tidak dibuang diam-diam, tetapi disimpan di `reject_penjualan` beserta alasannya.
- Kategori produk kosong menjadi `Tidak Diketahui`.
- Tabel target dibuat ulang setiap pipeline dijalankan, sehingga hasilnya selalu sama (idempotent).
