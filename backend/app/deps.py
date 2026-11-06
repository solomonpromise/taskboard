"""Request dependencies: who is asking, and is the request genuine? (book Chapters 7 and 11)."""
import secrets

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from . import security
from .db import get_db
from .errors import AppError
from .models import User
from .repositories import users as users_repo

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(security.SESSION_COOKIE)
    record = users_repo.get_active_session(db, security.hash_token(token)) if token else None
    if record is None:
        raise AppError(401, "not_signed_in", "Please sign in.")
    if request.method in UNSAFE_METHODS:
        sent = request.headers.get("X-CSRF-Token", "")
        if not secrets.compare_digest(sent, record.csrf_token):
            raise AppError(403, "csrf_failed", "This request could not be verified. Please reload the page.")
    return record.user
