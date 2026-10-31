import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "etl_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "datwar123")
DB_SOURCE_NAME = os.getenv("DB_SOURCE_NAME", "tokomaju_oltp")
DB_TARGET_NAME = os.getenv("DB_TARGET_NAME", "tokomaju_dwh")

DATA_RAW_DIR = BASE_DIR / os.getenv("DATA_RAW_DIR", "data/raw")
SQL_DIR = BASE_DIR / "sql"
OUTPUT_DIR = BASE_DIR / "output"


def get_db_url(db_name: str) -> URL:
    # URL.create otomatis meng-encode karakter khusus (@, :, /) pada password
    return URL.create(
        drivername="postgresql+psycopg2",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=db_name,
    )
