"""Structured JSON logs with a request ID on every line (book Chapter 32).

Never log passwords, tokens, cookies or request bodies.
"""
import json
import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname.lower(),
            "request_id": request_id_var.get(),
            "message": record.getMessage(),
        }
        entry.update(getattr(record, "fields", {}))
        if record.exc_info:
            entry["error"] = self.formatException(record.exc_info).splitlines()[-1]
        return json.dumps(entry)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("taskboard")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or f"r-{uuid.uuid4().hex[:8]}"
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers["X-Request-ID"] = request_id
        logging.getLogger("taskboard").info(
            "request",
            extra={"fields": {
                "request_id": request_id,
                "route": f"{request.method} {request.url.path}",
                "status": response.status_code,
                "ms": round((time.perf_counter() - started) * 1000),
            }},
        )
        return response
