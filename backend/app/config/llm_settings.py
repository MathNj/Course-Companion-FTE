"""
LLM Configuration Settings

Loads Anthropic API configuration from environment variables using pydantic-settings.
"""

from pydantic_settings import BaseSettings, Field
from typing import Optional


class LLMSettings(BaseSettings):
    """
    Anthropic Claude Sonnet 4.5 configuration loaded from environment.
    """

    # Anthropic API Configuration
    ANTHROPIC_API_KEY: str = Field(..., description="Anthropic API key (starts with sk-ant-api03-)")
    ANTHROPIC_MODEL: str = Field(default="claude-sonnet-4-5-20250929", description="Claude model version")
    ANTHROPIC_TIMEOUT: int = Field(default=30, description="API request timeout in seconds")
    ANTHROPIC_MAX_RETRIES: int = Field(default=3, description="Max retry attempts on failure")

    # Cost Monitoring
    LLM_COST_ALERT_THRESHOLD: float = Field(default=0.50, description="Alert threshold per student per month (USD)")
    LLM_COST_ALERT_EMAIL: Optional[str] = Field(None, description="Admin email for cost alerts")

    # Feature Flags
    ENABLE_ADAPTIVE_PATHS: bool = Field(default=True, description="Enable adaptive path generation")
    ENABLE_LLM_ASSESSMENTS: bool = Field(default=True, description="Enable LLM assessment grading")
    ENABLE_PHASE2_CACHING: bool = Field(default=True, description="Enable 24-hour caching for adaptive paths")

    # Rate Limits (per premium user per month)
    PREMIUM_ADAPTIVE_PATHS_LIMIT: int = Field(default=10, description="Monthly adaptive path quota")
    PREMIUM_ASSESSMENTS_LIMIT: int = Field(default=20, description="Monthly assessment quota")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance (singleton pattern)
_llm_settings: Optional[LLMSettings] = None


def get_llm_settings() -> LLMSettings:
    """Get or create global LLM settings instance."""
    global _llm_settings
    if _llm_settings is None:
        _llm_settings = LLMSettings()
    return _llm_settings
