-- Dijalankan di awal setiap pipeline agar skema target selalu sama dengan 01_create_tables.sql.
-- Aman karena seluruh isi data warehouse dibangun ulang dari sumber.
DROP TABLE IF EXISTS fakta_penjualan CASCADE;
DROP TABLE IF EXISTS reject_penjualan CASCADE;
DROP TABLE IF EXISTS dim_waktu CASCADE;
DROP TABLE IF EXISTS dim_produk CASCADE;
DROP TABLE IF EXISTS dim_pelanggan CASCADE;
