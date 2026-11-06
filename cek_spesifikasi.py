"""Menampilkan spesifikasi laptop dan versi tools untuk laporan (bagian 3.1).

Jalankan:  python cek_spesifikasi.py
Hasil juga tersimpan di output/spesifikasi.txt
"""
import ctypes
import os
import platform
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version

from sqlalchemy import text

from src.config import OUTPUT_DIR
from src.report import Report


def cpu_name() -> str:
    try:
        if platform.system() == "Windows":
            out = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
                capture_output=True, text=True, timeout=15).stdout.strip()
            if out:
                return out.splitlines()[0]
        elif platform.system() == "Linux":
            for baris in open("/proc/cpuinfo", encoding="utf-8"):
                if baris.startswith("model name"):
                    return baris.split(":", 1)[1].strip()
        elif platform.system() == "Darwin":
            return subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                  capture_output=True, text=True).stdout.strip()
    except Exception:
        pass
    return platform.processor() or "tidak terdeteksi"


def ram_gb() -> str:
    try:
        if platform.system() == "Windows":
            class MEM(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MEM()
            m.dwLength = ctypes.sizeof(MEM)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return f"{m.ullTotalPhys / 1024**3:.1f} GB"
        if platform.system() == "Linux":
            for baris in open("/proc/meminfo", encoding="utf-8"):
                if baris.startswith("MemTotal"):
                    return f"{int(baris.split()[1]) / 1024**2:.1f} GB"
        if platform.system() == "Darwin":
            n = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout)
            return f"{n / 1024**3:.1f} GB"
    except Exception:
        pass
    return "tidak terdeteksi"


def versi(paket: str) -> str:
    try:
        return version(paket)
    except PackageNotFoundError:
        return "belum terpasang"


def versi_postgres() -> str:
    try:
        from src.db import get_target_engine
        with get_target_engine().connect() as conn:
            return conn.execute(text("SHOW server_version")).scalar()
    except Exception as e:
        return f"tidak terhubung ({type(e).__name__}); cek manual dengan: psql --version"


def main():
    rep = Report()
    rep.add("SPESIFIKASI LAPTOP")
    rep.add(f"Sistem operasi : {platform.system()} {platform.release()} ({platform.version()})")
    rep.add(f"Arsitektur     : {platform.machine()}")
    rep.add(f"Prosesor       : {cpu_name()}")
    rep.add(f"Jumlah core    : {os.cpu_count()} (logical)")
    rep.add(f"RAM            : {ram_gb()}")
    rep.add("\nVERSI TOOLS")
    rep.add(f"Python         : {sys.version.split()[0]}")
    for p in ("pandas", "SQLAlchemy", "psycopg2-binary", "openpyxl", "python-dotenv", "tabulate"):
        rep.add(f"{p:<15}: {versi(p)}")
    rep.add(f"PostgreSQL     : {versi_postgres()}")
    path = rep.save(OUTPUT_DIR / "spesifikasi.txt")
    print(f"\nTersimpan di: {path}")


if __name__ == "__main__":
    main()
