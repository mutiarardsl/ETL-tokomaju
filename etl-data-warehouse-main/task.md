# **Tugas 1 — Eksplorasi Tools ETL**

Mata Kuliah Data Warehouse · Oct 20, 2026 · @niken

## **Deskripsi dan Tujuan**

Setiap kelompok mengeksplorasi satu tools ETL, membangun satu pipeline mini dari data mentah ke tabel dimensi dan fakta, lalu mempresentasikan kelebihan dan kekurangan tools tersebut. Tugas ini menjadi fondasi proyek data warehouse berikutnya, sehingga tools yang dipelajari di sini akan dipakai kelompok yang sama di tugas lanjutan.

Setelah menyelesaikan tugas ini, mahasiswa mampu:

1. Menjelaskan konsep *Extract, Transform, Load* (ETL) dan perbedaannya dengan ELT.  
2. Memasang dan mengonfigurasi satu tools ETL beserta koneksi ke database sumber dan target.  
3. Membangun pipeline sederhana yang membaca data dari beberapa format.

## **Ketentuan Umum**

Tugas dikerjakan berkelompok (4–5 orang), dengan waktu pengerjaan 1 minggu. Setiap kelompok memilih satu tools

| Pilihan | Tools ETL | Pendekatan | Database target yang disarankan |
| :---- | :---- | :---- | :---- |
| 1 | Pentaho Data Integration | GUI drag-and-drop | PostgreSQL / MySQL |
| 2 | Apache Hop | GUI drag-and-drop | PostgreSQL |
| 3 | KNIME Analytics Platform | Workflow berbasis node | PostgreSQL |
| 4 | SSIS (SQL Server Developer Edition) | GUI, ekosistem Microsoft | SQL Server |
| 5 | Python (pandas \+ SQLAlchemy) | Kode | PostgreSQL |
| 6 | Apache Airflow \+ Python | Kode \+ orkestrasi | PostgreSQL |
| 7 | Airbyte \+ dbt Core | ELT modern | PostgreSQL / BigQuery sandbox |

Ketentuan tambahan:

* Semua tools yang dipakai harus versi gratis atau open source.  
* Kelompok wajib menyebutkan versi tools, sistem operasi, dan spesifikasi laptop yang digunakan.  
* Penggunaan AI (ChatGPT, Claude, dan sejenisnya) diperbolehkan untuk membantu belajar, tetapi wajib dicantumkan di laporan bagian mana yang dibantu AI.

## **Dataset dan Skenario**

Semua kelompok memakai dataset yang sama agar hasilnya bisa dibandingkan secara adil. Skenarionya: toko ritel "TokoMaju" ingin menganalisis penjualan per produk, per pelanggan, dan per waktu.

Sumber data sengaja dibuat dalam tiga format berbeda:

| File | Format | Isi | Masalah yang sengaja disisipkan |
| :---- | :---- | :---- | :---- |
| penjualan.csv | CSV | Transaksi penjualan (id, tanggal, id\_produk, id\_pelanggan, qty, harga) | Format tanggal campur, baris duplikat, qty negatif |
| produk.xlsx | Excel | Master produk dan kategori | Nama kategori tidak konsisten ("Elektronik", "elektronik ", "ELEKTRONIK") |
| pelanggan (tabel MySQL/PostgreSQL) | Database | Master pelanggan dan kota | Nilai kota kosong, nomor telepon beragam format |

Target *star schema* minimal:

* dim\_waktu (tanggal, hari, bulan, kuartal, tahun)  
* dim\_produk (produk, kategori)  
* dim\_pelanggan (pelanggan, kota)  
* fakta\_penjualan (kunci ke ketiga dimensi, qty, total\_penjualan)

Catatan: dataset disiapkan dan dibagikan melalui LMS sebelum tugas dimulai.

## **Langkah Pengerjaan**

1. **Kajian tools.** Pelajari sejarah singkat, lisensi, arsitektur, dan komponen utama tools yang didapat.  
2. **Instalasi dan konfigurasi.** Pasang tools, siapkan database target, dan dokumentasikan langkahnya dengan tangkapan layar, termasuk kendala yang muncul dan cara mengatasinya.  
3. **Extract.** Buat koneksi ke ketiga sumber data (CSV, Excel, database).  
4. **Transform.** Terapkan transformasi berikut:  
   * Menghapus baris duplikat

## **Deliverable dan Pengumpulan**

Setiap kelompok mengumpulkan melalui LMS dalam satu folder terkompresi bernama Tugas1\_Kelompok\<nomor\>\_\<NamaTools\>.zip.

| No | Deliverable | Ketentuan |
| :---- | :---- | :---- |
| 1 | Laporan | PDF, maksimal 15 halaman: kajian tools, langkah instalasi lengkap dengan screenshoot dan penjelasan, desain pipeline ekstrak data, pembagian tugas anggota |
| 2 | Video Demo instalasi tools | Durasi maksimal 10 menit |

Nilai individu dapat disesuaikan berdasarkan pembagian tugas di laporan dan jawaban saat tanya jawab.

## **Referensi Awal**

Titik awal dokumentasi resmi untuk tiap tools; kelompok diharapkan mencari tutorial tambahan sendiri.

* [Pentaho Data Integration](https://pentaho.com/products/pentaho-data-integration/)  
* [Apache Hop](https://hop.apache.org/)  
* [KNIME Analytics Platform](https://www.knime.com/knime-analytics-platform)  
* [SQL Server Integration Services](https://learn.microsoft.com/en-us/sql/integration-services/sql-server-integration-services)  
* [pandas](https://pandas.pydata.org/docs/) dan [SQLAlchemy](https://docs.sqlalchemy.org/)  
* [Apache Airflow](https://airflow.apache.org/docs/)  
* [Airbyte](https://docs.airbyte.com/) dan [dbt Core](https://docs.getdbt.com/)