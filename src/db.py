import sys

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from src.config import (
    DATA_RAW_DIR,
    DB_HOST,
    DB_PORT,
    DB_SOURCE_NAME,
    DB_TARGET_NAME,
    DB_USER,
    SQL_DIR,
    get_db_url,
)


def get_source_engine() -> Engine:
    """Engine ke database sumber (berisi tabel pelanggan)."""
    return create_engine(get_db_url(DB_SOURCE_NAME))


def get_target_engine() -> Engine:
    """Engine ke database target (data warehouse star schema)."""
    return create_engine(get_db_url(DB_TARGET_NAME))


def ensure_database(db_name: str) -> bool:
    """Buat database bila belum ada. Mengembalikan True jika baru dibuat."""
    admin = create_engine(get_db_url("postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": db_name}
            ).scalar()
            if exists:
                return False
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            return True
    finally:
        admin.dispose()


def init_source_table(engine: Engine) -> bool:
    """Muat data/raw/pelanggan.sql ke database sumber bila tabel belum berisi data.
    Mengembalikan True jika tabel baru dimuat."""
    sql_file = DATA_RAW_DIR / "pelanggan.sql"
    if not sql_file.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {sql_file}")

    try:
        with engine.connect() as conn:
            if conn.execute(text("SELECT COUNT(*) FROM pelanggan")).scalar():
                return False
    except Exception:
        pass  # tabel belum ada

    sql_content = sql_file.read_text(encoding="utf-8")
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            cur.execute(sql_content)
        raw_conn.commit()
    finally:
        raw_conn.close()
    return True


def _run_sql_file(engine: Engine, path) -> None:
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            cur.execute(path.read_text(encoding="utf-8"))
        raw_conn.commit()
    finally:
        raw_conn.close()


def init_target_schema(engine: Engine) -> None:
    """Hapus lalu buat ulang tabel target dari file SQL (satu sumber kebenaran skema)."""
    _run_sql_file(engine, SQL_DIR / "00_drop_tables.sql")
    _run_sql_file(engine, SQL_DIR / "01_create_tables.sql")


def check_server() -> None:
    """Cek koneksi ke server PostgreSQL; beri pesan yang mudah dipahami bila gagal."""
    admin = create_engine(get_db_url("postgres"))
    try:
        with admin.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as e:
        pesan = str(e.orig).strip().splitlines()[0] if e.orig else str(e)
        print("GAGAL terhubung ke PostgreSQL.")
        print(f"  Alamat : {DB_HOST}:{DB_PORT}   User: {DB_USER}")
        print(f"  Pesan  : {pesan}")
        print("Periksa: (1) PostgreSQL / Docker sudah berjalan, (2) nilai di file .env "
              "(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD) sudah benar.")
        sys.exit(2)
    finally:
        admin.dispose()
