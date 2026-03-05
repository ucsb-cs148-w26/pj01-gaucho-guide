import json
import os
from typing import Optional


_firebase_ready = False


def _ensure_firebase_admin() -> bool:
    global _firebase_ready
    if _firebase_ready:
        return True

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

    if not service_account_json and not service_account_path:
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            if service_account_json:
                cred = credentials.Certificate(json.loads(service_account_json))
            else:
                cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)

        _firebase_ready = True
        return True
    except Exception as e:
        print(f"Firebase admin init for token verify failed: {e}")
        return False


def verify_firebase_id_token(id_token: str) -> Optional[dict]:
    if not id_token:
        return None
    if not _ensure_firebase_admin():
        return None

    try:
        from firebase_admin import auth

        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        print(f"Firebase token verification failed: {e}")
        return None


def firebase_admin_ready() -> bool:
    return _ensure_firebase_admin()
