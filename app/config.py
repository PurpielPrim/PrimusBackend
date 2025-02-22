from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv

# Pobiera zmienne z pliku .env
load_dotenv()

class Settings(BaseSettings):
    secret_key: str = Field(alias="AUTH_SECRET")
    algorithm: str
    database_url: str

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()