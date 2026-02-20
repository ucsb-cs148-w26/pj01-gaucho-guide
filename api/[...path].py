from fastapi import FastAPI
from fastapi.responses import JSONResponse

try:
    from api.index import app as imported_app

    class PrefixNormalizingApp:
        def __init__(self, inner_app):
            self.inner_app = inner_app
            self.prefixes = ("/api/main", "/api", "/main")

        async def __call__(self, scope, receive, send):
            if scope.get("type") == "http":
                path = scope.get("path", "") or "/"
                for prefix in self.prefixes:
                    if path == prefix or path.startswith(prefix + "/"):
                        new_path = path[len(prefix):] or "/"
                        scope = dict(scope)
                        scope["path"] = new_path
                        break
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
                "detail": "Backend bootstrap failed on Vercel.",
                "error": bootstrap_error,
                "path": path,
            },
        )
