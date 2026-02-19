from unittest.mock import MagicMock

from app.config import settings

_firebase_app = None


def init_firebase():
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    if not settings.firebase_credentials_path:
        # Development mode - no real Firebase
        _firebase_app = MagicMock()
        return _firebase_app

    import firebase_admin
    from firebase_admin import credentials

    cred = credentials.Certificate(settings.firebase_credentials_path)
    _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def verify_token(id_token: str) -> dict:
    """Verify a Firebase ID token and return decoded claims."""
    if not settings.firebase_credentials_path:
        # Development mode - return mock claims
        return {"uid": id_token, "email": f"{id_token}@dev.local"}

    from firebase_admin import auth

    decoded = auth.verify_id_token(id_token)
    return decoded
