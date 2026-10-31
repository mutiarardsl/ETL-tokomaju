# Panduan Refinement dan Menjalankan Pipeline ETL TokoMaju (CB 1 dan CB 2)

Dokumen ini memakai repository `etl-data-warehouse-main` sebagai dasar. Semua perubahan di bawah **sudah diterapkan** pada `etl-data-warehouse-refined.zip`, jadi langkah refinement berfungsi sebagai penjelasan apa yang berubah dan alasannya, agar setiap anggota bisa menjelaskannya saat presentasi.

**Yang sudah saya uji:** PostgreSQL 16.15, Python 3.12 dengan pandas 3.0.2 dan SQLAlchemy 2.1.6, serta pandas 2.2.3. Tujuh unit test lulus, pipeline dijalankan dua kali dengan hasil sama, dan 13 pemeriksaan otomatis lulus. **Belum saya uji:** Docker Compose (hanya saya baca) dan pandas 3.1.0 yang disebut di laporan Anda sebelumnya.

## 1. Kebutuhan tugas dibandingkan kode awal

CB 2 mencakup CB 1. Berikut hasil pencocokan antara soal dan kode awal.

| Kebutuhan soal | Kode awal | Status | Refinement |
| --- | --- | --- | --- |
| Extract dari CSV, Excel, database | Ada | Baik | CSV dan Excel dibaca sebagai teks; ada mode `run_cb1.py` |
| Koneksi ke database **sumber dan target** | Satu database untuk keduanya | Kurang jelas | Dua database: `tokomaju_oltp` dan `tokomaju_dwh` |
| Hapus baris duplikat | Ada, tanpa bukti | Perlu bukti | Laporan sebelum dan sesudah serta contoh baris |
| Seragamkan format tanggal | **Bug**: tanggal ISO tertukar bulan dan hari | Salah | `parse_tanggal` yang eksplisit |
| Tangani nilai kosong dan qty negatif | Dibuang tanpa jejak | Perlu jejak | Tabel `reject_penjualan` dengan alasan |
| Seragamkan kategori | Ada | Baik | Kategori kosong menjadi `Tidak Diketahui` |
| Kolom `total_penjualan` | Ada | Baik | Harga kosong tidak lagi menjadi 0 diam-diam |
| **Surrogate key** dimensi | Tidak ada (memakai ID bisnis) | **Kurang** | Kunci `waktu_key`, `produk_key`, `pelanggan_key` |
| Load dimensi dulu, lalu fakta | Ada | Baik | Dimensi dan fakta dimuat dalam transaksi |
| **Verifikasi** baris dan total sebelum dan sesudah | Hanya mencetak jumlah baris DataFrame | **Kurang** | `verify.py`: rekonsiliasi plus 13 pemeriksaan ke database |
| Query analisis per kategori per bulan | Per kategori dan per kota saja | Perlu | `sql/02_query_analisis.sql` |
| **Skrip SQL pembuatan tabel** (deliverable CB 2) | Tidak ada (tabel dibuat lewat kode) | **Kurang** | `sql/00_drop_tables.sql` dan `sql/01_create_tables.sql` |
| Bukti untuk laporan | Tidak ada | Perlu | Folder `output/` terisi otomatis |

## 2. Langkah refinement (berurutan)

### Langkah 1: pisahkan database sumber dan target

**File:** `.env.example`, `src/config.py`, `src/db.py`

Soal meminta koneksi ke database sumber dan target. Kode awal memakai satu database. Sekarang ada dua: `tokomaju_oltp` (berisi tabel `pelanggan`, nama ini sesuai komentar di `pelanggan.sql`) dan `tokomaju_dwh` (star schema). Perubahan pendukung:

- `ensure_database()` membuat database bila belum ada, sehingga tidak perlu langkah manual.
- `get_db_url()` memakai `URL.create`, sehingga password yang berisi `@`, `:`, atau `/` tidak lagi merusak koneksi.
- `check_server()` menampilkan pesan yang mudah dipahami bila PostgreSQL belum jalan, bukan tumpukan error panjang.
- `pymysql` dihapus dari `requirements.txt` karena tidak dipakai.

### Langkah 2: pindahkan DDL ke file SQL dan tambah surrogate key

**File:** `sql/00_drop_tables.sql`, `sql/01_create_tables.sql`, `src/db.py`

Deliverable CB 2 mewajibkan skrip SQL pembuatan tabel. Sekarang skema ditulis di file SQL dan **file itulah yang dijalankan pipeline**, jadi tidak ada dua versi skema yang bisa berbeda. Isi utamanya:

| Tabel | Surrogate key | Business key |
| --- | --- | --- |
| `dim_waktu` | `waktu_key` (angka yyyymmdd, misalnya 20251106) | `tanggal` (UNIQUE) |
| `dim_produk` | `produk_key` (IDENTITY) | `id_produk` (UNIQUE) |
| `dim_pelanggan` | `pelanggan_key` (IDENTITY) | `id_pelanggan` (UNIQUE) |
| `fakta_penjualan` | `fakta_key` (IDENTITY) | `id_transaksi` (UNIQUE) |

`fakta_penjualan` berisi tiga kunci asing (`waktu_key`, `produk_key`, `pelanggan_key`), `qty` dengan `CHECK (qty > 0)`, `harga_satuan`, dan `total_penjualan`. Tabel `reject_penjualan` menampung transaksi yang ditolak. Setiap pipeline dijalankan, tabel target dihapus lalu dibuat ulang, sehingga hasilnya selalu konsisten dengan file SQL.

### Langkah 3: baca CSV dan Excel sebagai teks

**File:** `src/extract.py`

`dtype=str` pada `read_csv` dan `read_excel` mencegah pandas mengubah tipe data secara diam-diam. Konversi angka dan tanggal dilakukan sengaja di tahap Transform. Tabel `pelanggan` dibaca dengan `read_sql` lewat engine SQLAlchemy.

### Langkah 4: perbaiki parsing tanggal dan catat baris yang ditolak

**File:** `src/transform/clean_sales.py`

**Bug.** Kode awal memakai `format='mixed', dayfirst=True` untuk semua tanggal. Opsi `dayfirst=True` ikut menukar bulan dan hari pada tanggal ISO. Contoh: `2025-11-06` terbaca 11 Juni. Dampaknya 486 dari 2.400 transaksi (20,2%) masuk ke bulan yang salah, dan bug ini tidak terlihat di verifikasi jumlah baris.

**Perbaikan.** Tanggal ISO dibaca eksplisit, sisanya dibaca hari-bulan-tahun:

```python
is_iso = s.map(lambda v: bool(v) and re.match(REGEX_ISO, v) is not None)
iso = pd.to_datetime(s.where(is_iso), format='%Y-%m-%d', errors='coerce')
lain = pd.to_datetime(s.where(~is_iso), format='mixed', dayfirst=True, errors='coerce')
return iso.fillna(lain)
```

Untuk tanggal bergaris miring atau strip, `dayfirst` memang tepat: dari 863 nilai, 492 pasti hari-bulan dan tidak ada yang pasti bulan-hari. Sebanyak 371 nilai yang ambigu diasumsikan hari-bulan, **tulis ini sebagai asumsi di laporan**.

**Baris ditolak dicatat, tidak dibuang diam-diam.** `clean_sales` kini mengembalikan empat hal: `bersih`, `reject`, `duplikat`, dan `stat` (angka rekonsiliasi). Alasan penolakan dinilai berurutan:

| Urutan | Alasan | Baris pada data ini |
| --- | --- | --- |
| 1 | tanggal tidak valid | 0 |
| 2 | id\_produk kosong | 0 |
| 3 | id\_pelanggan kosong | 25 |
| 4 | qty kosong | 0 |
| 5 | qty negatif atau nol | 24 |
| 6 | harga kosong | 0 |

Duplikat dihapus berdasarkan `id_transaksi` (kemunculan pertama dipertahankan). Saya cek bahwa tidak ada `id_transaksi` yang sama dengan isi berbeda, jadi aturan ini aman. Harga kosong sekarang menjadi NaN lalu ditolak, bukan menjadi 0 yang membuat total penjualan terlihat normal padahal salah.

### Langkah 5: rapikan produk dan pelanggan

**File:** `src/transform/clean_products.py`, `src/transform/clean_customers.py`

- Kategori produk kosong menjadi `Tidak Diketahui`. Kode awal mengisinya dengan `Kesehatan & Kecantikan`, sebuah tebakan yang berlaku untuk semua kategori kosong. Pada data ini hanya produk P032 yang terdampak.
- Spasi dirapikan lebih dulu, baru duplikat dibuang (43 produk menjadi 40).
- Kota kosong, singkatan (`Mlg`, `SDA`), dan variasi (`Kota Malang`) diseragamkan. Pelanggan dengan kota `Tidak Diketahui` ada 32.
- Nomor telepon yang tadinya dibersihkan lalu dibuang kini masuk ke `dim_pelanggan` dalam format `08xxxxxxxxxx`, kosong menjadi NULL.

### Langkah 6: bangun dim\_waktu lengkap dan kandidat fakta

**File:** `src/transform/build_star_schema.py`

`dim_waktu` kini berisi kalender lengkap dari tanggal pertama sampai terakhir (365 baris), bukan hanya tanggal yang punya transaksi. Hari dan nama bulan ditulis dalam bahasa Indonesia lewat kamus. Fungsi ini juga menyiapkan `fakta_stage`, yaitu transaksi bersih yang masih memakai ID bisnis, karena surrogate key produk dan pelanggan baru ada setelah dimensi dimuat.

### Langkah 7: muat dalam dua tahap dan petakan surrogate key

**File:** `src/load.py`, `main.py`

Urutannya penting:

1. `load_dimensions()` memuat `dim_waktu`, `dim_produk`, `dim_pelanggan` dalam satu transaksi. PostgreSQL membuat `produk_key` dan `pelanggan_key` otomatis.
2. `attach_surrogate_keys()` membaca kembali pasangan kunci dari dimensi lalu menggabungkannya ke fakta:

```python
dp = pd.read_sql('SELECT produk_key, id_produk FROM dim_produk', engine)
dc = pd.read_sql('SELECT pelanggan_key, id_pelanggan FROM dim_pelanggan', engine)
f = fakta_stage.merge(dp, on='id_produk', how='left').merge(dc, on='id_pelanggan', how='left')
```

Transaksi yang produk atau pelanggannya tidak ada di master (9 baris) dipisahkan ke reject dengan alasan `id_produk tidak ada di master`. 3. `load_fact_and_rejects()` memuat fakta dan tabel reject dalam satu transaksi.

Semua `to_sql` memakai `if_exists='append'` agar tabel dan constraint dari file SQL tetap berlaku.

### Langkah 8: verifikasi otomatis

**File:** `src/verify.py`

Soal meminta membandingkan jumlah baris dan total penjualan sebelum dan sesudah ETL. Karena ada duplikat dan data bermasalah, angkanya tidak boleh sama persis. Yang dibuktikan adalah rekonsiliasi:

| Tahap | Baris | Total penjualan |
| --- | --- | --- |
| Data mentah (penjualan.csv) | 2.445 | Rp 469.154.600 |
| dikurangi duplikat id\_transaksi | -45 | Rp -7.331.400 |
| dikurangi ditolak: data tidak valid | -49 | Rp -1.427.800 |
| dikurangi ditolak: tidak ada di master | -9 | Rp -1.206.700 |
| **Hasil di fakta\_penjualan (database)** | **2.342** | **Rp 459.188.700** |

Selain itu ada 13 pemeriksaan yang dihitung dari database sungguhan: rekonsiliasi baris dan nilai, jumlah fakta dan total di DB sama dengan yang dikirim pipeline, jumlah tiap dimensi, tidak ada fakta tanpa dimensi (waktu, produk, pelanggan), tidak ada `qty <= 0`, dan `total_penjualan = qty x harga_satuan` untuk semua baris. Hasilnya disimpan di `output/verifikasi.txt`, dan `main.py` berakhir dengan kode error bila ada pemeriksaan yang gagal.

### Langkah 9: query analisis

**File:** `sql/02_query_analisis.sql`, `src/analytics.py`

Query utamanya **total penjualan per kategori per bulan** (contoh yang disebut di soal). Tiga query disimpan di file SQL dan dibaca oleh `analytics.py`. Hasil per kategori per bulan dicetak sebagai tabel silang (juta rupiah) dan disimpan ke `output/analisis_kategori_per_bulan.csv`.

### Langkah 10: mode CB 1

**File:** `run_cb1.py`, `src/profiling.py`

CB 1 menuntut koneksi ke tiga sumber dan penghapusan duplikat. `python run_cb1.py` melakukan itu dan menyimpan buktinya di `output/cb1_extract_report.txt`: status koneksi dua database, jumlah baris, kolom, nilai kosong, tiga baris contoh dari tiap sumber, serta jumlah duplikat sebelum dan sesudah beserta contoh barisnya. Perhatikan bahwa nilai kosong dihitung termasuk teks kosong, jadi kota kosong tercatat 32, bukan 16 seperti yang tampak bila hanya memakai `isna()`.

### Langkah 11: unit test dan README

**File:** `tests/`, `README.md`

Tujuh unit test menjaga bug yang tadi ditemukan agar tidak kembali: tanggal ISO tidak tertukar, format tanggal lain, harga `Rp85.000`, duplikat dan alasan penolakan, kategori `Elektronik` yang ditulis tiga cara, serta kota dan telepon. README menjelaskan struktur dan cara menjalankan.

## 3. Cara menerapkan refinement

**Opsi A (disarankan): pakai zip hasil refinement.** Ekstrak `etl-data-warehouse-refined.zip`, lalu jalankan dari folder `etl-data-warehouse`. Data mentah sudah ada di `data/raw/`.

**Opsi B: terapkan ke repository sendiri.** Urutan yang aman: (1) `.env.example`, `config.py`, `db.py`; (2) file di `sql/`; (3) `extract.py`; (4) empat file di `src/transform/`; (5) `load.py`, `verify.py`, `analytics.py`, `report.py`, `profiling.py`; (6) `main.py` dan `run_cb1.py`; (7) `tests/`. Jalankan `python -m pytest -q` setelah langkah 4 untuk memastikan transformasi benar sebelum lanjut.

## 4. Menjalankan pipeline

### Langkah 1: siapkan lingkungan Python

Buka terminal di folder yang berisi `main.py`:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Di Linux atau macOS, aktivasinya `source .venv/bin/activate`. Pastikan terminal menampilkan `(.venv)`.

### Langkah 2: siapkan PostgreSQL (pilih salah satu)

- **PostgreSQL lokal:** pastikan service berjalan. User yang dipakai harus berhak membuat database (user `postgres` sudah berhak). Anda tidak perlu membuat database manual.
- **Docker:** `docker compose up -d`, lalu cek dengan `docker ps`. pgAdmin tersedia di `http://localhost:5050` (email `admin@tokomaju.com`, password `admin`).

### Langkah 3: buat file `.env`

```bash
copy .env.example .env
```

Di Linux atau macOS pakai `cp`. Ubah `DB_PASSWORD` agar sama dengan password PostgreSQL Anda. File `.env` tidak ikut terkemas di zip.

### Langkah 4: jalankan CB 1

```bash
python run_cb1.py
```

Hasil yang diharapkan pada bagian duplikat:

| Sumber | Sebelum | Sesudah | Duplikat |
| --- | --- | --- | --- |
| penjualan.csv (kunci `id_transaksi`) | 2.445 | 2.400 | 45 |
| produk.xlsx (kunci `id_produk`) | 43 | 40 | 3 |
| pelanggan (kunci `id_pelanggan`) | 180 | 180 | 0 |

Bukti tersimpan di `output/cb1_extract_report.txt`. Screenshot terminal dan file ini untuk laporan dan video.

### Langkah 5: jalankan CB 2

```bash
python main.py
```

Pipeline berjalan dalam lima tahap. Angka yang diharapkan:

| Tahap | Hasil |
| --- | --- |
| 1. Extract | penjualan 2.445, produk 43, pelanggan 180 baris |
| 2. Transform | penjualan 2.445 menjadi 2.351 valid (duplikat 45, ditolak 49); produk 40; pelanggan 180 |
| 3. Load dimensi | dim\_waktu 365, dim\_produk 40, dim\_pelanggan 180 |
| 4. Load fakta | fakta\_penjualan 2.342; reject\_penjualan 58 |
| 5. Verifikasi | `HASIL AKHIR: SEMUA PEMERIKSAAN LULUS` |

Rincian 58 baris reject: `id_pelanggan kosong` 25, `qty negatif atau nol` 24, `id_produk tidak ada di master` 9. Total penjualan per kategori yang diharapkan: Elektronik Rp 166.075.500, Fashion Rp 130.187.200, Olahraga Rp 62.484.200, Rumah Tangga Rp 42.884.000, Makanan & Minuman Rp 32.003.400, Kesehatan & Kecantikan Rp 19.183.900, Tidak Diketahui Rp 6.370.500.

Pemeriksaan cepat bahwa bug tanggal sudah hilang: transaksi `T00003` harus tercatat tanggal 2025-11-06 dan `T00014` tanggal 2025-11-02. Jumlah transaksi per bulan (Januari sampai Desember) harus 150, 185, 198, 267, 183, 196, 210, 163, 152, 158, 205, 275.

### Langkah 6: periksa hasil di database

Buka pgAdmin atau `psql` pada database `tokomaju_dwh`:

```sql
SELECT COUNT(*) FROM fakta_penjualan;   -- 2342
SELECT * FROM dim_produk ORDER BY produk_key LIMIT 5;
SELECT alasan, COUNT(*) FROM reject_penjualan GROUP BY alasan;
```

File bukti yang dihasilkan di folder `output/`: `cb1_extract_report.txt`, `verifikasi.txt`, `analisis_kategori_per_bulan.csv`.

### Langkah 7: jalankan ulang dan uji

Jalankan `python main.py` sekali lagi. Angkanya harus sama persis (pipeline idempotent). Lalu jalankan `python -m pytest -q`, harapannya `7 passed`.

### Masalah yang sering muncul

| Gejala | Penyebab | Solusi |
| --- | --- | --- |
| `GAGAL terhubung ke PostgreSQL` | PostgreSQL atau Docker belum jalan, atau `.env` salah | Jalankan service-nya, cek `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` |
| `No module named 'src'` | Dijalankan dari folder yang salah | Jalankan dari folder yang berisi `main.py` |
| `No module named ...` | Library belum terpasang | Aktifkan `.venv`, lalu `pip install -r requirements.txt` |
| `permission denied to create database` | User tidak berhak membuat database | Pakai user `postgres`, atau buat `tokomaju_oltp` dan `tokomaju_dwh` manual |
| Port 5432 bentrok dengan PostgreSQL lokal saat memakai Docker | Dua server memakai port sama | Ubah `DB_PORT=5433` di `.env` |
| `main.py` berakhir dengan kode 1 | Ada pemeriksaan verifikasi yang gagal | Baca bagian `PEMERIKSAAN OTOMATIS` di `output/verifikasi.txt` |

## 5. Bahan penjelasan untuk presentasi

| Tahap | Fungsi utama | Yang perlu dijelaskan |
| --- | --- | --- |
| Persiapan | `ensure_database`, `init_source_table`, `init_target_schema` | Dua database dibuat otomatis, tabel pelanggan dimuat ke sumber, skema target dibuat dari file SQL |
| Extract | `extract_sales_csv`, `extract_products_excel`, `extract_customers_db` | Tiga format dibaca ke DataFrame; CSV dan Excel sebagai teks agar tidak ada konversi diam-diam |
| Transform penjualan | `clean_sales` | Duplikat, tanggal campur, harga Rp, qty negatif, baris ditolak, `total_penjualan` |
| Transform master | `clean_products`, `clean_customers` | Kategori dan kota diseragamkan, telepon dinormalkan, duplikat dibuang |
| Star schema | `build_star_schema` | `dim_waktu` lengkap 365 hari, kandidat fakta |
| Load | `load_dimensions`, `attach_surrogate_keys`, `load_fact_and_rejects` | Dimensi dulu, kunci surrogate dari database, baru fakta |
| Verifikasi | `verify` | Rekonsiliasi baris dan nilai, 13 pemeriksaan ke database |
| Analisis | `run_analytics` | Total penjualan per kategori per bulan |

Pertanyaan yang pasti muncul dan jawabannya: **mengapa 2.445 menjadi 2.342?** Karena 45 duplikat, 24 qty tidak positif, 25 tanpa pelanggan, dan 9 produk yang tidak ada di master. **Mengapa fakta dimuat terakhir?** Fakta punya kunci asing ke dimensi dan butuh surrogate key yang baru dibuat setelah dimensi dimuat. **Apa itu SQLAlchemy Engine dan psycopg2?** Engine mengelola koneksi dan pool; psycopg2 adalah driver yang berbicara dengan PostgreSQL.

## 6. Pemetaan deliverable

### CB 1 (`Tugas1_Kelompok<nomor>_Python.zip`)

- **Laporan PDF (maks. 15 halaman):** kajian tools (sejarah, lisensi, arsitektur, komponen), langkah instalasi dengan screenshot dan kendala, desain pipeline extract (diagram dan hasil `run_cb1.py`), pembagian tugas, serta bagian yang dibantu AI. Cantumkan juga versi tools, sistem operasi, dan spesifikasi laptop.
- **Video demo instalasi (maks. 10 menit):** pasang Python dan PostgreSQL, buat venv dan `pip install`, isi `.env`, jalankan `python run_cb1.py`, tunjukkan hasil duplikat.

### CB 2 (`CB2_Kelompok<nomor>_Python.zip`)

- **Laporan PDF (maks. 30 halaman):** semua bagian CB 1 ditambah desain pipeline lengkap (diagram alur dan star schema), hasil verifikasi (tabel rekonsiliasi dan 13 pemeriksaan), query analisis, dan evaluasi tools.
- **File pipeline:** `main.py`, `run_cb1.py`, folder `src/`, `sql/`, `tests/`, `requirements.txt`, `.env.example`, `README.md`. Skrip SQL pembuatan tabel ada di `sql/01_create_tables.sql`.
- **Slide (maks. 10):** tools dan alasan pilih, arsitektur, masalah data, transformasi, star schema, rekonsiliasi, query analisis, evaluasi tools, pembagian tugas. Semua anggota harus berbicara.

### Bahan evaluasi tools (skala 1 sampai 5)

Nilai harus berasal dari pengalaman kelompok. Contoh bukti konkret dari proyek ini:

| Kriteria | Bukti yang bisa dipakai |
| --- | --- |
| Kemudahan instalasi | Jumlah menit dan langkah, kendala nyata (PATH, `psycopg2`, port 5432) dan solusinya |
| Kurva belajar | Butuh Python dasar; jam yang dibutuhkan sampai pipeline pertama jalan |
| Kelengkapan fitur transformasi | Tanggal campur, duplikat, kategori semuanya selesai dengan fungsi pandas; tetapi kelompok sempat terkena bug `dayfirst` pada tanggal ISO |
| Dokumentasi dan komunitas | Dokumentasi pandas dan SQLAlchemy lengkap; error mudah dicari solusinya |
| Performa | Pipeline 2.445 baris selesai di bawah satu detik; tetapi semua data dimuat ke memori sehingga perlu dibahas untuk data jauh lebih besar |
| Kecocokan skala industri | Tidak ada penjadwalan, monitoring, atau retry bawaan; perlu Airflow atau tools serupa untuk produksi |

## 7. Keputusan yang harus kelompok tetapkan dan tulis di laporan

| Keputusan | Pilihan di kode | Alternatif |
| --- | --- | --- |
| Qty negatif atau nol | Ditolak ke `reject_penjualan` | Dianggap retur, atau diubah ke nilai positif |
| Format tanggal ambigu (371 nilai) | Hari-bulan-tahun | Bulan-hari-tahun |
| Transaksi tanpa pelanggan (25) | Ditolak | Dipertahankan dengan pelanggan `Tidak Diketahui` |
| Produk tidak ada di master (9 baris) | Ditolak | Dibuat baris produk `Tidak Diketahui` |
| Kategori produk kosong | `Tidak Diketahui` | Diisi dari sumber lain |
| `dim_waktu` | Kalender lengkap 365 hari | Hanya tanggal yang punya transaksi |
| Skema target | Dibuat ulang tiap run | Dipertahankan dan di-upsert |

Catatan: jika kelompok memilih alternatif, angka di bagian 4 akan berubah, dan angka itulah yang harus dicantumkan di laporan.
