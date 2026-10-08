"""
Application configuration using Pydantic Settings
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Gemini Configuration
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash-exp"
    gemini_thinking_level: str = "medium"

    # Database
    database_url: str = "sqlite:///./data/cognishield.db"

    # Storage
    storage_dir: str = "./storage"
    max_image_size_mb: int = 20
    max_video_size_mb: int = 200
    max_video_duration_seconds: int = 120  # 2 minutes default

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Report Directory
    report_dir: str = "./storage/reports"

    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    # Demo Mode
    demo_mode: bool = False
    
    # Feature Flags
    enable_caching: bool = True
    enable_rule_engine: bool = True
    enable_guardrails: bool = True

    class Config:
        """Pydantic config"""
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"


settings = Settings()
