"""Supabase client initialization for SnapMend."""
from supabase import create_client, Client
from app.config import settings

def get_supabase() -> Client:
    """FastAPI dependency — returns the Supabase client using the secret key to bypass RLS."""
    return create_client(settings.supabase_url, settings.supabase_secret_key)

async def init_db():
    """No-op for Supabase REST API setup. Tables should be created in Supabase dashboard."""
    pass
