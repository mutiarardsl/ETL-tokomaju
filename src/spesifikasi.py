import sys, platform, pandas, sqlalchemy, psycopg2
print(platform.platform(), platform.processor())
print('Python', sys.version.split()[0])
print('pandas', pandas.__version__)
print('SQLAlchemy', sqlalchemy.__version__)
print('psycopg2', psycopg2.__version__)