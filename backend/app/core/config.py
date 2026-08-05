from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================
    # Application
    # ==========================

    APP_NAME: str = "AI Digital Twin"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ==========================
    # Security
    # ==========================

    SECRET_KEY: str = Field(...)

    # ==========================
    # Database
    # ==========================

    DATABASE_URL: str = Field(...)

    # ==========================
    # AI APIs
    # ==========================

    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None

    # ==========================
    # JWT
    # ==========================

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()