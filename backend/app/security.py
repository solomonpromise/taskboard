"""Passwords and sessions (book Chapter 11).

- Passwords are stored only as slow, salted hashes (Argon2 via pwdlib).
- Password policy follows NIST SP 800-63B-4 (2025): at least 15 characters for
  password-only sign-in, at least 64 allowed, no composition rules, block common
  and breached passwords, no forced periodic changes.
- Sessions: a random token in an HttpOnly, SameSite=Lax cookie; only its hash is stored.
- CSRF: each session has a token; the frontend sends it in X-CSRF-Token on every
  request that changes data, and deps.current_user checks it.
"""
import hashlib
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Response
from pwdlib import PasswordHash

from .config import settings

SESSION_COOKIE = "session"
CSRF_COOKIE = "csrf_token"
SESSION_DAYS = 30
MIN_PASSWORD_LENGTH = 15
MAX_PASSWORD_LENGTH = 128

_hasher = PasswordHash.recommended()
_common = set((Path(__file__).parent / "data" / "common_passwords.txt").read_text().split())


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _hasher.verify(password, password_hash)


def password_problem(password: str, email: str) -> str | None:
    """Return a user-facing reason the password is unacceptable, or None."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Use at least {MIN_PASSWORD_LENGTH} characters. A short phrase of a few words works well."
    if len(password) > MAX_PASSWORD_LENGTH:
        return f"Use at most {MAX_PASSWORD_LENGTH} characters."
    lowered = password.lower()
    local_part = email.split("@")[0].lower()
    if lowered in _common or (len(local_part) >= 4 and local_part in lowered):
        return "That password is too easy to guess. Try a longer, less common phrase."
    return None


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_session_tokens() -> tuple[str, str, datetime]:
    """Return (session token, CSRF token, expiry)."""
    expires = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    return secrets.token_urlsafe(32), secrets.token_urlsafe(24), expires


def set_session_cookies(response: Response, session_token: str, csrf_token: str) -> None:
    max_age = SESSION_DAYS * 24 * 3600
    response.set_cookie(SESSION_COOKIE, session_token, max_age=max_age, httponly=True,
                        secure=settings.cookie_secure, samesite="lax", path="/")
    # Readable by the frontend so it can echo it in the X-CSRF-Token header.
    response.set_cookie(CSRF_COOKIE, csrf_token, max_age=max_age, httponly=False,
                        secure=settings.cookie_secure, samesite="lax", path="/")


def clear_session_cookies(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")


class SignInLimiter:
    """Slow down password guessing: at most 5 failures per email in 15 minutes.

    In-memory, so per process; see docs/debt.md for the production plan.
    """

    def __init__(self, limit: int = 5, window_seconds: int = 900):
        self.limit, self.window = limit, window_seconds
        self._failures: dict[str, deque] = defaultdict(deque)

    def _prune(self, key: str) -> deque:
        failures = self._failures[key]
        while failures and failures[0] < time.monotonic() - self.window:
            failures.popleft()
        return failures

    def blocked(self, key: str) -> bool:
        return len(self._prune(key)) >= self.limit

    def record_failure(self, key: str) -> None:
        self._prune(key).append(time.monotonic())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)


sign_in_limiter = SignInLimiter()
