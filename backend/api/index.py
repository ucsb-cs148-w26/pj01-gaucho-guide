import os
import sys
from urllib.parse import parse_qs

from fastapi import FastAPI
from fastapi.responses import JSONResponse


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


try:
    from src.main import app as imported_app  # noqa: E402

    class ForwardedPathApp:
        def __init__(self, inner_app):
            self.inner_app = inner_app

        async def __call__(self, scope, receive, send):
            if scope.get("type") == "http":
                query_bytes = scope.get("query_string", b"")
                if query_bytes:
                    parsed = parse_qs(query_bytes.decode("utf-8"), keep_blank_values=True)
                    forwarded = parsed.get("__path")
                    if forwarded:
                        raw = forwarded[0].strip("/")
                        scope = dict(scope)
                        scope["path"] = f"/{raw}" if raw else "/"
            await self.inner_app(scope, receive, send)

    app = ForwardedPathApp(imported_app)
except Exception as e:  # pragma: no cover
    app = FastAPI()
    bootstrap_error = f"{type(e).__name__}: {e}"

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def _bootstrap_failed(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Backend bootstrap failed on Vercel (backend project).",
                "error": bootstrap_error,
                "path": path,
            },
        )
