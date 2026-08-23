from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    GEMINI_API_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: Optional[str] = None
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    GEMINI_GENERATION_MODEL: str = "gemini-3.6-flash"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    JWT_SECRET_KEY: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
