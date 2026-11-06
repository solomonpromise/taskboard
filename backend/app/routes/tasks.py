"""Task routes. HTTP only: identify the user, parse input, call the service, shape the response."""
import json
from datetime import date

from fastapi import APIRouter, Depends, Header, Query, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_user
from ..models import User
from ..repositories import labels as labels_repo
from ..repositories import tasks as tasks_repo
from ..services import tasks as tasks_service

router = APIRouter(prefix="/v1")


class TaskCreate(BaseModel):
    title: str = Field(max_length=1000)
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=1000)
    due_date: date | None = None
    is_done: bool | None = None


@router.get("/tasks")
def list_tasks(status: str = Query("open", pattern="^(open|done)$"), limit: int = Query(50, ge=1, le=100),
               cursor: int = Query(0, ge=0), user: User = Depends(current_user), db: Session = Depends(get_db)):
    items, next_cursor = tasks_service.list_tasks(db, user, done=(status == "done"), limit=limit, offset=cursor)
    return {"items": items, "next_cursor": next_cursor}


@router.get("/tasks/{task_id}")
def get_task(task_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    task = tasks_service.get_task(db, user, task_id)
    labels = labels_repo.labels_for_tasks(db, user.id, [task.id])[task.id]
    return tasks_service.task_view(task, user, labels=labels)


@router.post("/tasks", status_code=201)
def create_task(body: TaskCreate, user: User = Depends(current_user), db: Session = Depends(get_db),
                idempotency_key: str | None = Header(default=None, max_length=100)):
    # A repeated request with the same key returns the original result instead of a second task (Chapter 22).
    if idempotency_key:
        saved = tasks_repo.get_idempotent_response(db, user.id, idempotency_key)
        if saved is not None:
            return JSONResponse(json.loads(saved), status_code=201)
    task = tasks_service.create_task(db, user, title=body.title, due_date=body.due_date)
    view = tasks_service.task_view(task, user)
    if idempotency_key:
        tasks_repo.save_idempotent_response(db, user.id, idempotency_key, json.dumps(view))
    db.commit()
    return view


@router.patch("/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    changes = body.model_dump(exclude_unset=True)
    task = tasks_service.update_task(db, user, task_id, changes)
    db.commit()
    return tasks_service.task_view(task, user)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    tasks_service.delete_task(db, user, task_id)
    db.commit()
    return Response(status_code=204)
