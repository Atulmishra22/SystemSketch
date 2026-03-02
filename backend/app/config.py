"""
Application Configuration using Pydantic Settings V2
https://fastapi.tiangolo.com/advanced/settings/
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
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
    def CORS_ORIGINS(self) -> List[str]:
        """Returns list of allowed CORS origins"""
        return [self.FRONTEND_URL, "http://localhost:3000"]


# Global settings instance
settings = Settings()
