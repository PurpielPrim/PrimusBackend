from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_MJ3KxrU5QSGC@ep-fragrant-sky-a9rehxx8-pooler.gwc.azure.neon.tech:5432/neondb?sslmode=require"

# Testowanie połączenia
try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("Połączenie z bazą danych Neon udane!")
except Exception as e:
    print(f"Nie udało się połączyć z bazą danych: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
