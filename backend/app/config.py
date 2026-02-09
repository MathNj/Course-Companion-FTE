"""
Application Configuration

Loads environment variables and provides configuration settings.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Course Companion FTE"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database - with postgres:// to postgresql+asyncpg:// conversion for Fly.io
    @property
    def database_url(self) -> str:
        """Get database URL, converting postgres:// to postgresql+asyncpg:// for SQLAlchemy 2.0+"""
        db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/course_companion")

        # Convert postgres:// or postgresql:// to postgresql+asyncpg:// for async SQLAlchemy
        if db_url.startswith("postgres://"):
            # Replace postgres:// with postgresql+asyncpg://
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://"):
            # Add asyncpg driver
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        return db_url

    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis Cache
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-here-change-in-production-minimum-32-characters"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 43200  # 30 days
    jwt_refresh_token_expire_minutes: int = 43200  # 30 days

    # Cloudflare R2 Storage
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "course-companion-content"
    r2_endpoint: str = ""

    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:8000",
        "https://course-companion-web.fly.dev",
        "https://chat.openai.com",
        "https://chatgpt.com",
    ]
    cors_allow_credentials: bool = True

    # Content Configuration
    content_cache_ttl: int = 3600  # 1 hour
    chapter_count: int = 6

    # Rate Limiting
    rate_limit_per_minute: int = 100

    # Phase 2 Configuration (Optional)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    llm_cost_alert_threshold: float = 0.50


# Global settings instance
settings = Settings()
