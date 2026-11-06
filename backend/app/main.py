"""Taskboard API entry point."""
from fastapi import FastAPI

from .errors import install_error_handlers
from .logging_setup import RequestLogMiddleware, configure_logging
from .routes import auth, health

configure_logging()

app = FastAPI(title="Taskboard API", version="1.0.0")
app.add_middleware(RequestLogMiddleware)
install_error_handlers(app)
app.include_router(health.router)
app.include_router(auth.router)
