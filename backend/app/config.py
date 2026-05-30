"""Configuration management for SnapMend backend."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GCP Configuration
    gcp_project_id: str
    gcs_bucket_name: str
    bq_dataset: str
    bq_repair_history_table: str = "mcd_dataset.repair_history"
    bq_streets_table: str = "mcd_dataset.streets"
    bq_work_orders_table: str = "mcd_dataset.work_orders"

    # Gemini API Configuration
    gemini_api_key: str

    # Email Configuration
    resend_api_key: str
    notification_from_email: str
    notification_to_email: str

    # Frontend Configuration
    frontend_url: str = "http://localhost:5173"
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
