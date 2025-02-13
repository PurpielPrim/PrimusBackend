from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from .config import settings
from sqlalchemy import create_engine

# Zmień poniżej na swoje dane połączeniowe do Neon
DATABASE_MIGRATION = "postgresql+psycopg2://neondb_owner:npg_MJ3KxrU5QSGC@ep-fragrant-sky-a9rehxx8-pooler.gwc.azure.neon.tech:5432/neondb?sslmode=require"

# Testowanie połączenia
try:
    engine = create_engine(DATABASE_MIGRATION)
    connection = engine.connect()
    print("Połączenie z bazą danych Neon udane!")
except Exception as e:
    print(f"Nie udało się połączyć z bazą danych: {e}")

# SQLALCHEMY_DATABASE_URL = (
#     f'postgresql://{settingshost.database_username}:{settingshost.database_password}@'
#     f'{settingshost.database_hostname}:{settingshost.database_port}/{settingshost.database_name}'
# )
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_MJ3KxrU5QSGC@ep-fragrant-sky-a9rehxx8-pooler.gwc.azure.neon.tech:5432/neondb?sslmode=require"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
