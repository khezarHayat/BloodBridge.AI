"""
Application configuration using pydantic-settings.

Loads environment variables from .env file and provides a singleton
settings instance for the entire application.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWKS_URL: Optional[str] = None
    SUPABASE_AUTH_ISSUER: Optional[str] = None

    # JWT Configuration
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "ES256"
    JWT_ALGORITHMS: List[str] = ["ES256", "HS256"]

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173"

    # Application Configuration
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"
    APP_NAME: str = "BloodBridge API"
    APP_VERSION: str = "1.0.0"

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "20/minute"

    # Matching Engine
    MAX_MATCH_RESULTS: int = 20
    MIN_DONATION_INTERVAL_DAYS: int = 56

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list of origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def jwks_url(self) -> str:
        """Return configured or auto-derived JWKS endpoint."""
        if self.SUPABASE_JWKS_URL and self.SUPABASE_JWKS_URL.strip():
            return self.SUPABASE_JWKS_URL.strip()
        base = self.SUPABASE_URL.strip().rstrip("/")
        return f"{base}/auth/v1/.well-known/jwks.json" if base else ""

    @property
    def auth_issuer(self) -> str:
        """Return expected Supabase Auth issuer."""
        if self.SUPABASE_AUTH_ISSUER and self.SUPABASE_AUTH_ISSUER.strip():
            return self.SUPABASE_AUTH_ISSUER.strip()
        base = self.SUPABASE_URL.strip().rstrip("/")
        return f"{base}/auth/v1" if base else ""

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    model_config = {
        "env_file": Path(__file__).resolve().parent.parent.parent / ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()
