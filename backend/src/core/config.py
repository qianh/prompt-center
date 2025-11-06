"""
Configuration settings for Prompt Center backend.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./prompt_center.db"
    
    # Security
    ENCRYPTION_KEY: str = "default-encryption-key-change-me-in-production"
    
    # Development
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # LLM API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    
    class Config:
        env_file = ".env"


settings = Settings()
