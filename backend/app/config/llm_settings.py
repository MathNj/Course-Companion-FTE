"""
LLM Configuration Settings

Loads OpenAI API configuration from environment variables using pydantic-settings.
"""

from pydantic_settings import BaseSettings, Field
from typing import Optional


class LLMSettings(BaseSettings):
    """
    OpenAI GPT-4o-mini configuration loaded from environment.
    """

    # OpenAI API Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key (starts with sk-)")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="OpenAI model version")
    OPENAI_TIMEOUT: int = Field(default=30, description="API request timeout in seconds")
    OPENAI_MAX_RETRIES: int = Field(default=3, description="Max retry attempts on failure")

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
