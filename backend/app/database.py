"""Firebase client initialization for SnapMend."""
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import settings
import os

_db = None

def get_firestore():
    """FastAPI dependency — returns the Firestore client."""
    global _db
    if _db is None:
        if not firebase_admin._apps:
            cred_path = os.path.join(os.path.dirname(__file__), '..', settings.firebase_credentials_path)
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db

async def init_db():
    """No-op for Firestore setup. Collections are created automatically on write."""
    pass
