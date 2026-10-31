import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from tabulate import tabulate

from src.config import OUTPUT_DIR
from src.report import Report


def rupiah(x: float) -> str:
    return f"Rp {x:,.0f}".replace(",", ".")


def verify(engine: Engine, stat: dict, star: dict) -> bool:
    """Bandingkan data sebelum dan sesudah ETL, lalu cek ke database sungguhan."""
    rep = Report()

    def q(sql: str):
        with engine.connect() as conn:
            return conn.execute(text(sql)).scalar()

    n_fakta_db = int(q("SELECT COUNT(*) FROM fakta_penjualan"))
    total_fakta_db = float(q("SELECT COALESCE(SUM(total_penjualan), 0) FROM fakta_penjualan"))
    n_reject_db = int(q("SELECT COUNT(*) FROM reject_penjualan"))

    n_reject_total = stat["n_reject"] + stat["n_reject_master"]
    total_reject_total = stat["total_reject"] + stat["total_reject_master"]

    rep.add("=" * 70)
    rep.add("REKONSILIASI: DATA MENTAH -> TABEL FAKTA")
    rep.add("=" * 70)
    rows = [
        ["Data mentah (penjualan.csv)", stat["n_mentah"], rupiah(stat["total_mentah"])],
        ["(-) Duplikat id_transaksi", -stat["n_duplikat"], rupiah(-stat["total_duplikat"])],
        ["(-) Ditolak: data tidak valid", -stat["n_reject"], rupiah(-stat["total_reject"])],
        ["(-) Ditolak: tidak ada di master", -stat["n_reject_master"], rupiah(-stat["total_reject_master"])],
        ["= Hasil di fakta_penjualan (DB)", n_fakta_db, rupiah(total_fakta_db)],
    ]
    rep.add(tabulate(rows, headers=["Tahap", "Baris", "Total penjualan"], tablefmt="simple"))

    if stat["reject_per_alasan"] or stat["reject_master_per_alasan"]:
        rep.add("\nRincian baris yang ditolak:")
        gabung = {**stat["reject_per_alasan"], **stat["reject_master_per_alasan"]}
        rep.add(tabulate(sorted(gabung.items(), key=lambda kv: -kv[1]),
                         headers=["Alasan", "Baris"], tablefmt="simple"))

    cek = [
        ("Baris: mentah = duplikat + ditolak + fakta",
         stat["n_mentah"], stat["n_duplikat"] + n_reject_total + n_fakta_db),
        ("Nilai: mentah = duplikat + ditolak + fakta",
         round(stat["total_mentah"], 2),
         round(stat["total_duplikat"] + total_reject_total + total_fakta_db, 2)),
        ("Jumlah fakta di DB = jumlah yang dikirim pipeline", stat["n_fakta"], n_fakta_db),
        ("Total fakta di DB = total yang dikirim pipeline",
         round(stat["total_fakta"], 2), round(total_fakta_db, 2)),
        ("Baris reject_penjualan di DB", n_reject_total, n_reject_db),
        ("Baris dim_waktu di DB", len(star["dim_waktu"]), int(q("SELECT COUNT(*) FROM dim_waktu"))),
        ("Baris dim_produk di DB", len(star["dim_produk"]), int(q("SELECT COUNT(*) FROM dim_produk"))),
        ("Baris dim_pelanggan di DB", len(star["dim_pelanggan"]), int(q("SELECT COUNT(*) FROM dim_pelanggan"))),
        ("Fakta tanpa dimensi waktu", 0, int(q(
            "SELECT COUNT(*) FROM fakta_penjualan f LEFT JOIN dim_waktu d ON d.waktu_key=f.waktu_key WHERE d.waktu_key IS NULL"))),
        ("Fakta tanpa dimensi produk", 0, int(q(
            "SELECT COUNT(*) FROM fakta_penjualan f LEFT JOIN dim_produk d ON d.produk_key=f.produk_key WHERE d.produk_key IS NULL"))),
        ("Fakta tanpa dimensi pelanggan", 0, int(q(
            "SELECT COUNT(*) FROM fakta_penjualan f LEFT JOIN dim_pelanggan d ON d.pelanggan_key=f.pelanggan_key WHERE d.pelanggan_key IS NULL"))),
        ("Fakta dengan qty <= 0", 0, int(q("SELECT COUNT(*) FROM fakta_penjualan WHERE qty <= 0"))),
        ("Fakta dengan total <> qty x harga", 0, int(q(
            "SELECT COUNT(*) FROM fakta_penjualan WHERE total_penjualan <> qty * harga_satuan"))),
    ]

    rep.add("\n" + "=" * 70)
    rep.add("PEMERIKSAAN OTOMATIS")
    rep.add("=" * 70)
    hasil = []
    semua_lulus = True
    for nama, diharapkan, aktual in cek:
        ok = diharapkan == aktual
        semua_lulus &= ok
        tampil = (lambda v: f"{v:,.0f}".replace(",", ".")) if isinstance(diharapkan, float) else str
        hasil.append([("LULUS" if ok else "GAGAL"), nama, tampil(diharapkan), tampil(aktual)])
    rep.add(tabulate(hasil, headers=["Status", "Pemeriksaan", "Harapan", "Aktual"], tablefmt="simple",
                     colalign=("left", "left", "right", "right")))
    rep.add("\nHASIL AKHIR: " + ("SEMUA PEMERIKSAAN LULUS" if semua_lulus else "ADA PEMERIKSAAN YANG GAGAL"))

    rep.save(OUTPUT_DIR / "verifikasi.txt")
    return semua_lulus
