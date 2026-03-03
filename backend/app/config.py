"""
Application Configuration using Pydantic Settings V2
https://fastapi.tiangolo.com/advanced/settings/
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Environment: 'development' uses SQLite, 'production' uses PostgreSQL
    ENVIRONMENT: str = "development"

    # Database
    # Development default: SQLite (no setup needed)
    # Production: set to postgresql+asyncpg://user:pass@host:5432/dbname
    DATABASE_URL: Optional[str] = None

    # JWT Authentication
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # Server
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def db_url(self) -> str:
        """Returns the effective database URL based on environment."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.ENVIRONMENT == "production":
            raise ValueError(
                "DATABASE_URL must be set in production environment."
            )
        # Default: SQLite for local development
        return "sqlite+aiosqlite:///./systemsketch.db"

    @property
    def is_sqlite(self) -> bool:
        """True when the effective DB URL targets SQLite."""
        return self.db_url.startswith("sqlite")

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Returns list of allowed CORS origins"""
        return [self.FRONTEND_URL, "http://localhost:3000"]


# Global settings instance
settings = Settings()
