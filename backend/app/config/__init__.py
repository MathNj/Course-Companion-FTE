"""
Configuration package for Course Companion FTE.

This package contains all configuration modules for the application.
"""

import importlib.util
from pathlib import Path

# Load settings from config.py module (sibling to this package)
config_path = Path(__file__).parent.parent / "config.py"
spec = importlib.util.spec_from_file_location("app.config_module", config_path)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
settings = config_module.settings

# Import LLM settings from the package
from app.config.llm_settings import LLMSettings, get_llm_settings

__all__ = ["settings", "LLMSettings", "get_llm_settings"]
