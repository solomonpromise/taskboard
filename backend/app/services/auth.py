"""Business rules for accounts and sign-in (book Chapter 11)."""
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.orm import Session

from .. import security
from ..errors import AppError
from ..models import User
from ..repositories import users as users_repo

GENERIC_SIGN_IN_ERROR = "Email or password is incorrect."


def _normalise_email(email: str) -> str:
    return email.strip().lower()


def _check_time_zone(time_zone: str) -> str:
    try:
        ZoneInfo(time_zone)
    except (ZoneInfoNotFoundError, ValueError):
        raise AppError(400, "invalid_time_zone", "Unknown time zone.") from None
    return time_zone


def sign_up(db: Session, *, name: str, email: str, password: str, time_zone: str) -> User:
    email = _normalise_email(email)
    name = name.strip()
    if not name:
        raise AppError(400, "invalid_name", "Please add your name.")
    problem = security.password_problem(password, email)
    if problem:
        raise AppError(400, "weak_password", problem)
    if users_repo.get_by_email(db, email):
        raise AppError(409, "email_taken", "An account with this email already exists. Try signing in.")
    return users_repo.insert_user(
        db, name=name, email=email, password_hash=security.hash_password(password),
        time_zone=_check_time_zone(time_zone),
    )


def sign_in(db: Session, *, email: str, password: str) -> User:
    email = _normalise_email(email)
    if security.sign_in_limiter.blocked(email):
        raise AppError(429, "too_many_attempts", "Too many attempts. Please wait a few minutes and try again.")
    user = users_repo.get_by_email(db, email)
    if user is None or not security.verify_password(password, user.password_hash):
        security.sign_in_limiter.record_failure(email)
        # Same message whether the email or the password was wrong (Chapter 11).
        raise AppError(401, "invalid_credentials", GENERIC_SIGN_IN_ERROR)
    security.sign_in_limiter.reset(email)
    return user


def start_session(db: Session, user: User) -> tuple[str, str]:
    session_token, csrf_token, expires = security.new_session_tokens()
    users_repo.insert_session(db, token_hash=security.hash_token(session_token), user_id=user.id,
                              csrf_token=csrf_token, expires_at=expires)
    return session_token, csrf_token
