# File: api/[...path].py

import os
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Repo root (one level above /api)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Your python backend folder (adjust if yours differs)
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

# Ensure `backend/` is importable so `from src.main import app` works
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    # This should be your FastAPI instance: app = FastAPI() in backend/src/main.py
    from src.main import app as imported_app  # noqa: E402

    class StripApiPrefix:
        """
        Vercel will route requests to this function under /api/*.
        Your FastAPI routes are defined as /chat/*, /rag/*, etc.
        Strip the leading /api so FastAPI sees /chat/*, /rag/*.
        """
        def __init__(self, inner_app):
            self.inner_app = inner_app

        async def __call__(self, scope, receive, send):
            if scope.get("type") == "http":
                path = scope.get("path", "") or "/"
                if path == "/api" or path.startswith("/api/"):
                    scope = dict(scope)
                    scope["path"] = path[4:] or "/"  # remove "/api"
            await self.inner_app(scope, receive, send)

    app = StripApiPrefix(imported_app)

except Exception as e:  # pragma: no cover
    # If anything fails during import/boot, return JSON so you can see the real error in prod
    app = FastAPI()
    bootstrap_error = f"{type(e).__name__}: {e}"

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def _bootstrap_failed(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Backend bootstrap failed on Vercel.",
                "error": bootstrap_error,
                "path": path,
            },
        )