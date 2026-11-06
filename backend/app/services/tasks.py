"""Business rules for tasks (book Chapters 3, 7 and 22). No HTTP and no SQL here."""
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from ..errors import AppError
from ..models import Task, User
from ..repositories import labels as labels_repo
from ..repositories import tasks as tasks_repo
from .dates import is_overdue, user_today

MAX_TITLE = 200
MAX_OPEN_TASKS = 500


def _clean_title(title: str) -> str:
    title = (title or "").strip()
    if not title:
        raise AppError(400, "invalid_title", "Please add a title.")
    if len(title) > MAX_TITLE:
        raise AppError(400, "invalid_title", f"Titles can be at most {MAX_TITLE} characters.")
    return title


def _check_due_date(due_date: date | None, user: User) -> date | None:
    if due_date is not None and due_date < user_today(user.time_zone):
        raise AppError(400, "invalid_due_date", "Due dates can be today or later.")
    return due_date


def task_view(task: Task, user: User, today: date | None = None, labels: list[dict] | None = None) -> dict:
    today = today or user_today(user.time_zone)
    return {
        "id": task.id,
        "title": task.title,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "is_done": task.is_done,
        "is_overdue": (not task.is_done) and is_overdue(task.due_date, today),
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "labels": labels if labels is not None else [],
    }


def list_tasks(db: Session, user: User, *, done: bool, limit: int, offset: int) -> tuple[list[dict], int | None]:
    rows = tasks_repo.list_for_owner(db, user.id, done=done, limit=limit + 1, offset=offset)
    today = user_today(user.time_zone)
    next_offset = offset + limit if len(rows) > limit else None
    rows = rows[:limit]
    labels = labels_repo.labels_for_tasks(db, user.id, [t.id for t in rows])
    return [task_view(t, user, today, labels[t.id]) for t in rows], next_offset


def get_task(db: Session, user: User, task_id: int) -> Task:
    task = tasks_repo.get_owned(db, task_id, user.id)
    if task is None:
        # 404, not 403: don't even confirm that someone else's task exists (Chapter 7).
        raise AppError(404, "not_found", "Task not found.")
    return task


def create_task(db: Session, user: User, *, title: str, due_date: date | None) -> Task:
    open_count = len(tasks_repo.list_for_owner(db, user.id, done=False, limit=MAX_OPEN_TASKS + 1, offset=0))
    if open_count >= MAX_OPEN_TASKS:
        raise AppError(400, "limit_reached", f"You can have at most {MAX_OPEN_TASKS} open tasks.")
    return tasks_repo.insert(db, owner_id=user.id, title=_clean_title(title),
                             due_date=_check_due_date(due_date, user))


def update_task(db: Session, user: User, task_id: int, changes: dict) -> Task:
    task = get_task(db, user, task_id)
    if "title" in changes:
        task.title = _clean_title(changes["title"])
    if "due_date" in changes and changes["due_date"] != task.due_date:
        task.due_date = _check_due_date(changes["due_date"], user)
    if "is_done" in changes and changes["is_done"] != task.is_done:
        task.is_done = bool(changes["is_done"])
        task.completed_at = datetime.now(timezone.utc) if task.is_done else None
    db.flush()
    return task


def delete_task(db: Session, user: User, task_id: int) -> None:
    if tasks_repo.delete_owned(db, task_id, user.id) == 0:
        raise AppError(404, "not_found", "Task not found.")
