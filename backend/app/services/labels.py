"""Business rules for labels (book Chapters 25-28)."""
from sqlalchemy.orm import Session

from ..errors import AppError
from ..models import Label, User
from ..repositories import labels as labels_repo
from . import tasks as tasks_service

MAX_NAME = 40


def _get_label(db: Session, user: User, label_id: int) -> Label:
    label = labels_repo.get_owned(db, label_id, user.id)
    if label is None:
        raise AppError(404, "not_found", "Label not found.")
    return label


def create_label(db: Session, user: User, name: str) -> Label:
    name = (name or "").strip()
    if not name or len(name) > MAX_NAME:
        raise AppError(400, "invalid_label", f"Label names need 1 to {MAX_NAME} characters.")
    if labels_repo.get_by_name(db, user.id, name):
        raise AppError(409, "label_exists", "You already have a label with that name.")
    return labels_repo.insert(db, user.id, name)


def delete_label(db: Session, user: User, label_id: int) -> None:
    if labels_repo.delete_owned(db, label_id, user.id) == 0:
        raise AppError(404, "not_found", "Label not found.")


def attach(db: Session, user: User, task_id: int, label_id: int) -> None:
    task = tasks_service.get_task(db, user, task_id)  # 404 unless it is my task
    label = _get_label(db, user, label_id)  # 404 unless it is my label
    if not labels_repo.link_exists(db, task.id, label.id):  # attaching twice is harmless
        labels_repo.link(db, task.id, label.id)


def detach(db: Session, user: User, task_id: int, label_id: int) -> None:
    tasks_service.get_task(db, user, task_id)
    labels_repo.unlink(db, task_id, label_id)
