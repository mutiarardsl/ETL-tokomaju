import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Database Settings
DB_TYPE = os.getenv("DB_TYPE", "postgresql")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tokomaju_dwh")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Paths
DATA_RAW_DIR = BASE_DIR / os.getenv("DATA_RAW_DIR", "data/raw")
DATA_SQL_DIR = BASE_DIR / os.getenv("DATA_SQL_DIR", "data/sql")

DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_SQL_DIR.mkdir(parents=True, exist_ok=True)


def get_db_url() -> str:
    return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
