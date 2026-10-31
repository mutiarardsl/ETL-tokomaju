-- name: kategori_per_bulan
SELECT dw.tahun, dw.bulan, dw.nama_bulan, dp.kategori,
       COUNT(*)               AS transaksi,
       SUM(f.qty)             AS unit_terjual,
       SUM(f.total_penjualan) AS total_penjualan
FROM fakta_penjualan f
JOIN dim_waktu  dw ON dw.waktu_key  = f.waktu_key
JOIN dim_produk dp ON dp.produk_key = f.produk_key
GROUP BY dw.tahun, dw.bulan, dw.nama_bulan, dp.kategori
ORDER BY dw.tahun, dw.bulan, total_penjualan DESC;

-- name: total_per_kategori
SELECT dp.kategori,
       COUNT(*)               AS transaksi,
       SUM(f.qty)             AS unit_terjual,
       SUM(f.total_penjualan) AS total_penjualan
FROM fakta_penjualan f
JOIN dim_produk dp ON dp.produk_key = f.produk_key
GROUP BY dp.kategori
ORDER BY total_penjualan DESC;

-- name: total_per_kota
SELECT dpl.kota,
       COUNT(*)               AS transaksi,
       SUM(f.total_penjualan) AS total_penjualan
FROM fakta_penjualan f
JOIN dim_pelanggan dpl ON dpl.pelanggan_key = f.pelanggan_key
GROUP BY dpl.kota
ORDER BY total_penjualan DESC;
