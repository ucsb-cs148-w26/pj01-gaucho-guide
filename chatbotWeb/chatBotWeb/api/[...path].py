import os
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse


def _find_repo_root(start_dir: str) -> str:
    current = os.path.abspath(start_dir)
    for _ in range(8):
        if os.path.isdir(os.path.join(current, "backend")):
            return current
        current = os.path.dirname(current)
    return os.path.abspath(start_dir)


REPO_ROOT = _find_repo_root(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


try:
    from src.main import app as imported_app  # noqa: E402

    class PrefixNormalizingApp:
        def __init__(self, inner_app):
            self.inner_app = inner_app
            self.prefixes = ("/api/index", "/api/main", "/api", "/main")

        def _normalized(self, path: str) -> str:
            for prefix in self.prefixes:
                if path == prefix or path.startswith(prefix + "/"):
                    return path[len(prefix):] or "/"
            return path or "/"

        async def __call__(self, scope, receive, send):
            if scope.get("type") == "http":
                path = scope.get("path", "") or "/"
                normalized_path = self._normalized(path)

                if normalized_path == "/_debug/path":
                    debug_payload = {
                        "original_path": path,
                        "normalized_path": normalized_path,
                        "method": scope.get("method"),
                        "headers": {
                            (k.decode("latin-1") if isinstance(k, (bytes, bytearray)) else str(k)):
                            (v.decode("latin-1") if isinstance(v, (bytes, bytearray)) else str(v))
                            for k, v in scope.get("headers", [])
                        },
                    }
                    response = JSONResponse(status_code=200, content=debug_payload)
                    await response(scope, receive, send)
                    return

                if normalized_path != path:
                    scope = dict(scope)
                    scope["path"] = normalized_path

            await self.inner_app(scope, receive, send)

    app = PrefixNormalizingApp(imported_app)
except Exception as e:  # pragma: no cover
    app = FastAPI()
    bootstrap_error = f"{type(e).__name__}: {e}"

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def _bootstrap_failed(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Backend bootstrap failed on Vercel (frontend-root fallback).",
                "error": bootstrap_error,
                "path": path,
            },
        )
