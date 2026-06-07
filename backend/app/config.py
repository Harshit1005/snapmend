"""Configuration management for SnapMend backend."""
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini API — required, get free key at https://ai.google.dev
    gemini_api_key: str

    # GCP Configuration — optional for local SQLite-only dev
    gcp_project_id: Optional[str] = None
    gcs_bucket_name: Optional[str] = None
    bq_dataset: Optional[str] = "mcd_dataset"
    bq_repair_history_table: Optional[str] = "mcd_dataset.repair_history"
    bq_streets_table: Optional[str] = "mcd_dataset.streets"
    bq_work_orders_table: Optional[str] = "mcd_dataset.work_orders"

    # Email Configuration — optional, skip if no Resend key
    resend_api_key: Optional[str] = None
    notification_from_email: Optional[str] = "noreply@snapmend.app"
    notification_to_email: Optional[str] = None

    # SQLite path (relative to backend root)
    sqlite_db_path: str = "snapmend.db"

    # Frontend Configuration
    frontend_url: str = "http://localhost:5173"
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
