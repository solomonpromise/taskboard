"""Data access for labels. Every query includes the owner."""
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..models import Label, Task, TaskLabel


def list_for_owner(db: Session, owner_id: int) -> list[Label]:
    return list(db.scalars(select(Label).where(Label.owner_id == owner_id).order_by(Label.name)))


def get_owned(db: Session, label_id: int, owner_id: int) -> Label | None:
    return db.scalar(select(Label).where(Label.id == label_id, Label.owner_id == owner_id))


def get_by_name(db: Session, owner_id: int, name: str) -> Label | None:
    return db.scalar(select(Label).where(Label.owner_id == owner_id, Label.name == name))


def insert(db: Session, owner_id: int, name: str) -> Label:
    label = Label(owner_id=owner_id, name=name)
    db.add(label)
    db.flush()
    return label


def delete_owned(db: Session, label_id: int, owner_id: int) -> int:
    return db.execute(delete(Label).where(Label.id == label_id, Label.owner_id == owner_id)).rowcount


def link_exists(db: Session, task_id: int, label_id: int) -> bool:
    return db.get(TaskLabel, (task_id, label_id)) is not None


def link(db: Session, task_id: int, label_id: int) -> None:
    db.add(TaskLabel(task_id=task_id, label_id=label_id))


def unlink(db: Session, task_id: int, label_id: int) -> None:
    db.execute(delete(TaskLabel).where(TaskLabel.task_id == task_id, TaskLabel.label_id == label_id))


def labels_for_tasks(db: Session, owner_id: int, task_ids: list[int]) -> dict[int, list[dict]]:
    """All labels for many tasks in ONE query, never one query per task (Chapter 23 walkthrough)."""
    if not task_ids:
        return {}
    rows = db.execute(
        select(TaskLabel.task_id, Label.id, Label.name)
        .join(Label, Label.id == TaskLabel.label_id)
        .join(Task, Task.id == TaskLabel.task_id)
        .where(TaskLabel.task_id.in_(task_ids), Task.owner_id == owner_id)
        .order_by(Label.name)
    )
    result: dict[int, list[dict]] = {task_id: [] for task_id in task_ids}
    for task_id, label_id, name in rows:
        result[task_id].append({"id": label_id, "name": name})
    return result
