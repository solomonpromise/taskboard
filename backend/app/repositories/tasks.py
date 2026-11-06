"""Data access for tasks. Every query that touches a task includes its owner (book Chapter 10)."""
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..models import IdempotencyKey, Task


def list_for_owner(db: Session, owner_id: int, *, done: bool, limit: int, offset: int) -> list[Task]:
    query = select(Task).where(Task.owner_id == owner_id, Task.is_done == done)
    if done:
        query = query.order_by(Task.completed_at.desc(), Task.id.desc())
    else:
        # Soonest due first; undated tasks last (acceptance criterion, Chapter 3).
        query = query.order_by(Task.due_date.is_(None), Task.due_date, Task.id)
    return list(db.scalars(query.limit(limit).offset(offset)))


def get_owned(db: Session, task_id: int, owner_id: int) -> Task | None:
    return db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == owner_id))


def insert(db: Session, *, owner_id: int, title: str, due_date) -> Task:
    task = Task(owner_id=owner_id, title=title, due_date=due_date)
    db.add(task)
    db.flush()
    return task


def delete_owned(db: Session, task_id: int, owner_id: int) -> int:
    return db.execute(delete(Task).where(Task.id == task_id, Task.owner_id == owner_id)).rowcount


def get_idempotent_response(db: Session, user_id: int, key: str) -> str | None:
    record = db.get(IdempotencyKey, (user_id, key))
    return record.response_json if record else None


def save_idempotent_response(db: Session, user_id: int, key: str, response_json: str) -> None:
    db.add(IdempotencyKey(user_id=user_id, key=key, response_json=response_json))
