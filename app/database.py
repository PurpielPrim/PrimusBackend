from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .config import settings

DATABASE_URL = settings.database_url

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
