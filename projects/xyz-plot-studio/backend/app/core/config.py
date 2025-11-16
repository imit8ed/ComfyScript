"""
Application configuration using pydantic-settings.
"""

from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    # ComfyUI Configuration
    comfyui_url: str = Field(
        default="http://localhost:8188", description="ComfyUI server URL"
    )
    comfyui_client_id: str = Field(
        default="xyz-plot-studio", description="Client ID for ComfyUI"
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./xyz_studio.db", description="Database connection URL"
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # File Storage
    upload_dir: str = Field(default="./data/uploads", description="Upload directory")
    output_dir: str = Field(default="./data/outputs", description="Output directory")
    max_file_size_mb: int = Field(default=10, description="Max file size in MB")

    # Experiment Limits
    max_images_per_experiment: int = Field(
        default=500, description="Maximum images per experiment"
    )
    max_concurrent_experiments: int = Field(
        default=5, description="Maximum concurrent experiments"
    )

    # Wandb Configuration
    wandb_api_key: str = Field(default="", description="Wandb API key")
    wandb_entity: str = Field(default="", description="Wandb entity/username")
    wandb_project: str = Field(
        default="xyz-plot-studio", description="Wandb project name"
    )

    # Security
    secret_key: str = Field(
        default="change-me-in-production", description="Secret key for JWT"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
