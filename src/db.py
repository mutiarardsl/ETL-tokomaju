import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

def make_engine(dbname):
    url = URL.create(
        'postgresql+psycopg2',
        username=os.getenv('DB_USER', 'etl_user'),
        password=os.getenv('DB_PASS'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=dbname,
    )
    return create_engine(url)

src_engine = make_engine('tokomaju_src')
dwh_engine = make_engine('tokomaju_dwh')

if __name__ == '__main__':
    for nama, eng in [('SUMBER', src_engine), ('DWH', dwh_engine)]:
        with eng.connect() as conn:
            print(nama, '->', conn.execute(text('SELECT version()')).scalar())