from fastapi import FastAPI
from fastapi.responses import JSONResponse

try:
    from api.index import app as imported_app
    app = imported_app
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

