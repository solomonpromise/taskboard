"""Taskboard API entry point."""
from fastapi import FastAPI

from .routes import health

app = FastAPI(title="Taskboard API", version="1.0.0")
app.include_router(health.router)
