"""Configuration management using environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Server
    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=8000)
    
    # Tableau
    tableau_server: str = Field(...)  # Required
    tableau_site_id: str = Field(default="")
    tableau_pat_name: str = Field(...)  # Required
    tableau_pat_secret: str = Field(...)  # Required
    tableau_project_name: str = Field(default="Default")
    
    # Files
    default_file_directory: Path = Field(default=Path.home() / "Downloads")
    
    # Ollama
    ollama_model: str = Field(default="llama3.1:8b")
    
    # Logging
    log_level: str = Field(default="INFO")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


# Create global settings instance
settings = Settings()