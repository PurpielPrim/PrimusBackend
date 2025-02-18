from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Pobiera zmienne z pliku .env
load_dotenv()

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
