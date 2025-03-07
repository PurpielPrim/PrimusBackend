from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Application settings and environment variables configuration
    Attributes:
        secret_key: Secret key for JWT token generation
        algorithm: Algorithm used for JWT token encryption
        database_url: Database connection string
    """
    secret_key: str = Field(alias="AUTH_SECRET")
    algorithm: str
    database_url: str

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()