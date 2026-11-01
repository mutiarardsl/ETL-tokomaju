"""Menampilkan data SEBELUM dan SESUDAH transform: ringkasan jumlah baris + contoh baris nyata.

Dipanggil dari main.py setelah tahap Transform (sebelum Load).
Hasil dicetak ke layar dan disimpan di output/before_after.txt (bukti untuk laporan).
"""
import pandas as pd
from tabulate import tabulate

from src.config import OUTPUT_DIR
from src.report import Report


def _v(val) -> str:
    """Tampilkan nilai apa adanya (dengan tanda kutip agar spasi terlihat); kosong = NULL."""
    return "NULL" if pd.isna(val) else repr(str(val))


def _ringkasan(rep, raw_sales, sales, raw_products, products, raw_customers, customers):
    st = sales.stat
    rows = [
        ["penjualan.csv", len(raw_sales), st["n_bersih"], len(raw_sales) - st["n_bersih"],
         f"duplikat {st['n_duplikat']}, ditolak {st['n_reject']}"],
        ["produk.xlsx", len(raw_products), len(products), len(raw_products) - len(products),
         f"duplikat {len(raw_products) - len(products)}"],
        ["pelanggan (DB)", len(raw_customers), len(customers), len(raw_customers) - len(customers),
         f"duplikat {len(raw_customers) - len(customers)}"],
    ]
    rep.add("RINGKASAN JUMLAH BARIS (SEBELUM -> SESUDAH TRANSFORM)")
    rep.add(tabulate(rows, headers=["Sumber", "Sebelum", "Sesudah", "Dibuang", "Keterangan"],
                     tablefmt="simple"))
    rep.add(f"Total penjualan sebelum: Rp {st['total_mentah']:,.0f} | "
            f"sesudah (baris valid): Rp {st['total_bersih']:,.0f}".replace(",", "."))
    rep.add("Catatan: baris penjualan yang valid masih bisa ditolak saat Load jika produk/pelanggannya "
            "tidak ada di master. Angka akhir fakta ada di output/verifikasi.txt.")


def _contoh_penjualan(rep, raw, sales):
    bersih = sales.bersih.set_index("id_transaksi")
    reject = sales.reject.set_index("id_transaksi")
    dup_ids = set(sales.duplikat["id_transaksi"])

    tgl = raw["tanggal"]
    jenis = [
        ("Tanggal ISO, hari <= 12 (rawan tertukar)",
         tgl.str.match(r"^\d{4}-\d{2}-\d{2}$", na=False)
         & (pd.to_numeric(tgl.str[8:10], errors="coerce") <= 12), bersih.index),
        ("Tanggal hari/bulan/tahun", tgl.str.match(r"^\d{2}[/-]\d{2}[/-]\d{4}$", na=False), bersih.index),
        ("Tanggal dengan nama bulan", tgl.str.contains("[A-Za-z]", na=False), bersih.index),
        ("Harga memakai 'Rp'", raw["harga_satuan"].str.contains("Rp", na=False), bersih.index),
        ("Baris duplikat", raw.duplicated(subset="id_transaksi", keep="first"), list(dup_ids)),
        ("Qty negatif atau nol", pd.to_numeric(raw["qty"], errors="coerce") <= 0, reject.index),
        ("id_pelanggan kosong", raw["id_pelanggan"].isna(), reject.index),
    ]

    rep.add("\nCONTOH BARIS PENJUALAN: SEBELUM -> SESUDAH")
    for label, mask, boleh in jenis:
        ids = raw.loc[mask & raw["id_transaksi"].isin(boleh), "id_transaksi"]
        if ids.empty:
            continue
        tid = ids.iloc[0]
        r = raw[raw["id_transaksi"] == tid].iloc[0]
        rep.add(f"\n[{label}]  {tid}")
        rep.add(f"  Sebelum : tanggal={_v(r['tanggal'])}  qty={_v(r['qty'])}  "
                f"harga_satuan={_v(r['harga_satuan'])}  id_pelanggan={_v(r['id_pelanggan'])}")
        if label == "Baris duplikat":
            rep.add("  Sesudah : DIHAPUS (id_transaksi sama dengan baris sebelumnya, kemunculan pertama dipertahankan)")
        elif tid in reject.index:
            rep.add(f"  Sesudah : DITOLAK, alasan: {reject.loc[tid, 'alasan']} (disimpan di reject_penjualan)")
        else:
            b = bersih.loc[tid]
            rep.add(f"  Sesudah : tanggal='{b['tanggal']:%Y-%m-%d}'  qty={b['qty']}  "
                    f"harga_satuan={b['harga_satuan']:.0f}  total_penjualan={b['total_penjualan']:.0f}  "
                    "(lolos transform)")


def _contoh_produk(rep, raw, products):
    rp = raw.copy()
    rp["id_produk"] = rp["id_produk"].astype(str).str.strip()
    after = products.set_index("id_produk")["kategori"]

    rows, seen = [], set()
    for _, r in rp.iterrows():
        sebelum = r["kategori"]
        kunci = "NULL" if pd.isna(sebelum) else str(sebelum)
        if r["id_produk"] not in after.index or kunci in seen:
            continue
        sesudah = after[r["id_produk"]]
        if kunci != sesudah:
            seen.add(kunci)
            rows.append([r["id_produk"], _v(sebelum), sesudah])
        if len(rows) >= 7:
            break

    rep.add("\nCONTOH PRODUK: KATEGORI SEBELUM -> SESUDAH")
    rep.add(tabulate(rows, headers=["id_produk", "kategori sebelum", "kategori sesudah"], tablefmt="simple"))
    dup = rp[rp.duplicated(subset="id_produk", keep="first")]["id_produk"].tolist()
    rep.add(f"Baris produk duplikat yang dihapus: {', '.join(dup) if dup else 'tidak ada'}")


def _contoh_pelanggan(rep, raw, customers):
    rc = raw.copy()
    rc["id_pelanggan"] = rc["id_pelanggan"].astype(str).str.strip()
    gabung = rc.merge(customers, on="id_pelanggan", suffixes=("_awal", "_baru")).head(6)

    rep.add("\nCONTOH PELANGGAN: SEBELUM -> SESUDAH")
    for _, r in gabung.iterrows():
        rep.add(f"{r['id_pelanggan']} | kota {_v(r['kota_awal'])} -> {_v(r['kota_baru'])}"
                f" | telepon {_v(r['telepon_awal'])} -> {_v(r['telepon_baru'])}"
                f" | jenis_kelamin {_v(r['jenis_kelamin_awal'])} -> {_v(r['jenis_kelamin_baru'])}")


def tampilkan_before_after(raw_sales, sales, raw_products, products, raw_customers, customers):
    rep = Report()
    rep.add("=" * 70)
    rep.add("DATA SEBELUM DAN SESUDAH TRANSFORM")
    rep.add("=" * 70)
    _ringkasan(rep, raw_sales, sales, raw_products, products, raw_customers, customers)
    _contoh_penjualan(rep, raw_sales, sales)
    _contoh_produk(rep, raw_products, products)
    _contoh_pelanggan(rep, raw_customers, customers)
    path = rep.save(OUTPUT_DIR / "before_after.txt")
    print(f"\nTersimpan di: {path}")
