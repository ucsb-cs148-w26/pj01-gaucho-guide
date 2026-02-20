import os
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


try:
    from src.main import app as imported_app  # noqa: E402

    class StripApiPrefix:
        def __init__(self, inner_app):
            self.inner_app = inner_app
            self.prefixes = ("/api/main", "/api/index", "/api")

        async def __call__(self, scope, receive, send):
            if scope.get("type") == "http":
                path = scope.get("path", "") or "/"
                for prefix in self.prefixes:
                    if path == prefix or path.startswith(prefix + "/"):
                        scope = dict(scope)
                        scope["path"] = path[len(prefix):] or "/"
                        break
            await self.inner_app(scope, receive, send)

    app = StripApiPrefix(imported_app)
except Exception as e:  # pragma: no cover
    app = FastAPI()
    bootstrap_error = f"{type(e).__name__}: {e}"

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def _bootstrap_failed(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Backend bootstrap failed on Vercel (frontend-root).",
                "error": bootstrap_error,
                "path": path,
            },
        )
