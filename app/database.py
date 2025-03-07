from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Creates a database session and handles cleanup
    Yields:
        SessionLocal: Database session for dependency injection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()