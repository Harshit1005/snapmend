"""Configuration management for SnapMend backend."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List

# Resolve .env path relative to this file's location (backend/app/config.py)
_backend_dir = Path(__file__).resolve().parent.parent
_env_file_path = _backend_dir / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini API — required, get free key at https://ai.google.dev
    gemini_api_key: str

    # Firebase Configuration
    firebase_credentials_path: str = "firebase-key.json"

    # Frontend Configuration
    frontend_url: str = "http://localhost:5173"
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = str(_env_file_path)
        case_sensitive = False


settings = Settings()

