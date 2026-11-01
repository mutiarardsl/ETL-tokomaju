from sqlalchemy import (
    create_engine,
    text,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
)
from sqlalchemy.engine import Engine
from src.config import get_db_url, DATA_RAW_DIR


def get_engine() -> Engine:
    return create_engine(get_db_url(), echo=False)


def init_source_table(engine: Engine):
    sql_file = DATA_RAW_DIR / "pelanggan.sql"
    if not sql_file.exists():
        return

    try:
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM pelanggan")).scalar()
            if count and count > 0:
                return
    except Exception:
        pass

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            cur.execute(sql_content)
        raw_conn.commit()
    finally:
        raw_conn.close()


def init_target_star_schema(engine: Engine):
    metadata = MetaData()

    Table(
        "dim_waktu",
        metadata,
        Column("tanggal", Date, primary_key=True),
        Column("hari", String(50), nullable=False),
        Column("bulan", Integer, nullable=False),
        Column("kuartal", Integer, nullable=False),
        Column("tahun", Integer, nullable=False),
    )

    Table(
        "dim_produk",
        metadata,
        Column("id_produk", String(50), primary_key=True),
        Column("produk", String(255), nullable=False),
        Column("kategori", String(100), nullable=False),
    )

    Table(
        "dim_pelanggan",
        metadata,
        Column("id_pelanggan", String(50), primary_key=True),
        Column("pelanggan", String(255), nullable=False),
        Column("kota", String(100), nullable=False),
    )

    Table(
        "fakta_penjualan",
        metadata,
        Column("id_penjualan", String(50), primary_key=True),
        Column("tanggal", Date, ForeignKey("dim_waktu.tanggal"), nullable=False),
        Column("id_produk", String(50), ForeignKey("dim_produk.id_produk"), nullable=False),
        Column("id_pelanggan", String(50), ForeignKey("dim_pelanggan.id_pelanggan"), nullable=False),
        Column("qty", Integer, nullable=False),
        Column("total_penjualan", Numeric(15, 2), nullable=False),
        Column("metode_bayar", String(50), nullable=True),
    )

    metadata.create_all(engine)
