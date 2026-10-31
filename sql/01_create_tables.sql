-- Star schema TokoMaju (database target: tokomaju_dwh)
-- Surrogate key: dim_waktu memakai yyyymmdd; dim_produk dan dim_pelanggan memakai IDENTITY.
-- id_produk dan id_pelanggan tetap disimpan sebagai business key (UNIQUE).

CREATE TABLE dim_waktu (
    waktu_key   INT          PRIMARY KEY,
    tanggal     DATE         NOT NULL UNIQUE,
    hari        VARCHAR(10)  NOT NULL,
    bulan       SMALLINT     NOT NULL,
    nama_bulan  VARCHAR(12)  NOT NULL,
    kuartal     SMALLINT     NOT NULL,
    tahun       SMALLINT     NOT NULL
);

CREATE TABLE dim_produk (
    produk_key  INT          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_produk   VARCHAR(20)  NOT NULL UNIQUE,
    produk      VARCHAR(255) NOT NULL,
    kategori    VARCHAR(100) NOT NULL
);

CREATE TABLE dim_pelanggan (
    pelanggan_key  INT          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_pelanggan   VARCHAR(20)  NOT NULL UNIQUE,
    pelanggan      VARCHAR(255) NOT NULL,
    kota           VARCHAR(100) NOT NULL,
    telepon        VARCHAR(25)
);

CREATE TABLE fakta_penjualan (
    fakta_key        BIGINT        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_transaksi     VARCHAR(30)   NOT NULL UNIQUE,
    waktu_key        INT           NOT NULL REFERENCES dim_waktu (waktu_key),
    produk_key       INT           NOT NULL REFERENCES dim_produk (produk_key),
    pelanggan_key    INT           NOT NULL REFERENCES dim_pelanggan (pelanggan_key),
    metode_bayar     VARCHAR(30),
    qty              INT           NOT NULL CHECK (qty > 0),
    harga_satuan     NUMERIC(15,2) NOT NULL,
    total_penjualan  NUMERIC(15,2) NOT NULL
);

-- Baris transaksi yang ditolak beserta alasannya (jejak audit, bukan bagian star schema)
CREATE TABLE reject_penjualan (
    id_transaksi    VARCHAR(30),
    tanggal_mentah  TEXT,
    id_produk       TEXT,
    id_pelanggan    TEXT,
    qty             TEXT,
    harga_satuan    TEXT,
    alasan          VARCHAR(60) NOT NULL
);
