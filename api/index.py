import os
import sys
from urllib.parse import parse_qs

from fastapi import FastAPI
from fastapi.responses import JSONResponse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from src.main import app as imported_app  # noqa: E402

    class PrefixNormalizingApp:
        def __init__(self, inner_app):
            self.inner_app = inner_app
            self.prefixes = ("/api/index", "/api/main", "/api", "/main")

        def _path_from_forwarded_query(self, scope) -> str | None:
            query_bytes = scope.get("query_string", b"")
            if not query_bytes:
                return None
            parsed = parse_qs(query_bytes.decode("utf-8"), keep_blank_values=True)
            forwarded = parsed.get("__path")
            if not forwarded:
                return None
            raw = forwarded[0].strip("/")
            return f"/{raw}" if raw else "/"

        async def __call__(self, scope, receive, send):
            if scope.get("type") == "http":
                path = scope.get("path", "") or "/"
                # When Vercel rewrites /api/:path* -> /api?__path=:path*,
                # reconstruct the original subpath for FastAPI routing.
                forwarded_path = self._path_from_forwarded_query(scope)
                if forwarded_path is not None:
                    scope = dict(scope)
                    scope["path"] = forwarded_path
                    await self.inner_app(scope, receive, send)
                    return
                for prefix in self.prefixes:
                    if path == prefix or path.startswith(prefix + "/"):
                        new_path = path[len(prefix):] or "/"
                        scope = dict(scope)
                        scope["path"] = new_path
                        break
            await self.inner_app(scope, receive, send)

    app = PrefixNormalizingApp(imported_app)
except Exception as e:  # pragma: no cover
    # Fallback app so Vercel surfaces import/bootstrap errors as JSON.
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
