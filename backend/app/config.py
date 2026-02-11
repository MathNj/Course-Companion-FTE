"""
Application Configuration

Loads environment variables and provides configuration settings.
"""

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
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

    # Database - store raw URL for conversion (mapped from DATABASE_URL env var)
    database_url_raw: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/course_companion",
        alias="DATABASE_URL"
    )

    # Database - with postgres:// to postgresql+asyncpg// conversion for Fly.io
    @property
    def database_url(self) -> str:
        """Get database URL, converting postgres:// to postgresql+asyncpg:// for SQLAlchemy 2.0+"""
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

        db_url = self.database_url_raw

        # Convert postgres:// or postgresql:// to postgresql+asyncpg:// for async SQLAlchemy
        if db_url.startswith("postgres://"):
            # Replace postgres:// with postgresql+asyncpg://
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://"):
            # Add asyncpg driver
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Handle query parameters for different database providers
        parsed = urlparse(db_url)

        if "flycast-databases.com" in db_url or ".fly.io" in db_url:
            # Remove ALL query parameters for Fly.io internal databases
            db_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                "",  # Remove query string
                parsed.fragment
            ))
        elif "neon.tech" in db_url:
            # For Neon, remove sslmode and channel_binding from URL (SSL is handled via connect_args)
            query_params = parse_qs(parsed.query)
            # Remove unsupported parameters - SSL is handled via connect_args in database.py
            query_params.pop("channel_binding", None)
            query_params.pop("sslmode", None)
            new_query = urlencode(query_params, doseq=True) if query_params else ""
            db_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))

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
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:8000",
        "http://192.168.100.57:3000",
        "http://192.168.100.57:3001",
        "http://192.168.100.57:3002",
        "http://192.168.100.57:3003",
        "http://192.168.100.57:3004",
        "http://192.168.100.57:3005",
        "https://course-companion-web.fly.dev",
        "https://course-companion-fte.fly.dev",
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
