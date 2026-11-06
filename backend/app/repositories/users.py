"""Data access for users and sessions. The only place these tables are queried."""
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..models import SessionRecord, User


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def insert_user(db: Session, *, name: str, email: str, password_hash: str, time_zone: str) -> User:
    user = User(name=name, email=email, password_hash=password_hash, time_zone=time_zone)
    db.add(user)
    db.flush()
    return user


def insert_session(db: Session, *, token_hash: str, user_id: int, csrf_token: str, expires_at: datetime) -> None:
    db.add(SessionRecord(token_hash=token_hash, user_id=user_id, csrf_token=csrf_token, expires_at=expires_at))


def get_active_session(db: Session, token_hash: str) -> SessionRecord | None:
    record = db.get(SessionRecord, token_hash)
    if record is None:
        return None
    expires = record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=timezone.utc)
    return record if expires > datetime.now(timezone.utc) else None


def delete_session(db: Session, token_hash: str) -> None:
    db.execute(delete(SessionRecord).where(SessionRecord.token_hash == token_hash))
