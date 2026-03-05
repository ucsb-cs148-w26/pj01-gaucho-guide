import json
import os
from datetime import datetime, timezone
from typing import Any, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FirebaseChatHistoryManager:
    """Firestore-backed chat storage keyed by user email.

    Data model:
      users/{email}/chats/{chat_session_id}
        - title, created_at, last_updated
      users/{email}/chats/{chat_session_id}/messages/{auto_id}
        - role, content, timestamp
        - etc.
    """

    def __init__(self):
        self.enabled = False
        self.db = None

        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

        if not service_account_json and not service_account_path:
            return

        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            if not firebase_admin._apps:
                if service_account_json:
                    cred_dict = json.loads(service_account_json)
                    cred = credentials.Certificate(cred_dict)
                else:
                    cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)

            self.db = firestore.client()
            self.enabled = True
        except Exception as e:
            print(f"FirebaseChatHistoryManager init failed: {e}")
            self.enabled = False

    def _chat_ref(self, user_email: str, chat_session_id: str):
        return self.db.collection("users").document(user_email).collection("chats").document(chat_session_id)

    def save_message(self, user_email: str, chat_session_id: str, role: str, content: str):
        if not self.enabled or not user_email or not chat_session_id:
            return

        now = _utc_now()
        chat_ref = self._chat_ref(user_email, chat_session_id)

        # Keep title stable once set (first user message).
        title = None
        if role == "human":
            clean = (content or "").strip().replace("\n", " ")
            title = clean[:80] if clean else "New Chat"

        payload: dict[str, Any] = {
            "last_updated": now,
            "updated_at_iso": now.isoformat(),
        }
        if title:
            payload["title"] = title
        if not chat_ref.get().exists:
            payload["created_at"] = now
            payload["created_at_iso"] = now.isoformat()
            if not title:
                payload["title"] = "New Chat"

        chat_ref.set(payload, merge=True)

        chat_ref.collection("messages").add(
            {
                "role": role,
                "content": content,
                "timestamp": now,
                "timestamp_iso": now.isoformat(),
            }
        )

    def list_sessions(self, user_email: str, limit: int = 30) -> list[dict[str, Any]]:
        if not self.enabled or not user_email:
            return []

        docs = (
            self.db.collection("users")
            .document(user_email)
            .collection("chats")
            .order_by("last_updated", direction="DESCENDING")
            .limit(limit)
            .stream()
        )

        out: list[dict[str, Any]] = []
        for d in docs:
            data = d.to_dict() or {}
            out.append(
                {
                    "chat_session_id": d.id,
                    "title": data.get("title", "New Chat"),
                    "last_updated": data.get("updated_at_iso") or "",
                }
            )
        return out

    def get_messages(self, user_email: str, chat_session_id: str, limit: int = 300) -> list[dict[str, str]]:
        if not self.enabled or not user_email or not chat_session_id:
            return []

        docs = (
            self._chat_ref(user_email, chat_session_id)
            .collection("messages")
            .order_by("timestamp", direction="ASCENDING")
            .limit(limit)
            .stream()
        )

        out: list[dict[str, str]] = []
        for d in docs:
            data = d.to_dict() or {}
            out.append({"role": str(data.get("role", "")), "content": str(data.get("content", ""))})
        return out
