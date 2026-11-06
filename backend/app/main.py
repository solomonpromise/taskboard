"""Taskboard API entry point.

In development, Vite serves the frontend on :5173 and forwards API calls here.
In production, this one process serves both the API and the built frontend (frontend/dist).
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .errors import AppError, install_error_handlers
from .logging_setup import RequestLogMiddleware, configure_logging
from .routes import auth, health, labels, tasks

configure_logging()

app = FastAPI(title="Taskboard API", version="1.0.0")
app.add_middleware(RequestLogMiddleware)
install_error_handlers(app)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(labels.router)

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if path.startswith("v1/"):
            raise AppError(404, "not_found", "No such endpoint.")
        file = FRONTEND_DIST / path
        if path and file.is_file() and FRONTEND_DIST in file.resolve().parents:
            return FileResponse(file)
        # index.html must never be cached, or browsers keep loading an old release's assets.
        # (Files in /assets have content hashes in their names, so they can be cached safely.)
        return FileResponse(FRONTEND_DIST / "index.html", headers={"Cache-Control": "no-cache"})
