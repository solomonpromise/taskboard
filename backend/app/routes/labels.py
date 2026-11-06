"""Label routes."""
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_user
from ..models import User
from ..repositories import labels as labels_repo
from ..services import labels as labels_service

router = APIRouter(prefix="/v1")


class LabelCreate(BaseModel):
    name: str = Field(max_length=200)


class AttachIn(BaseModel):
    label_id: int


@router.get("/labels")
def list_labels(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"items": [{"id": l.id, "name": l.name} for l in labels_repo.list_for_owner(db, user.id)]}


@router.post("/labels", status_code=201)
def create_label(body: LabelCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    label = labels_service.create_label(db, user, body.name)
    db.commit()
    return {"id": label.id, "name": label.name}


@router.delete("/labels/{label_id}", status_code=204)
def delete_label(label_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    labels_service.delete_label(db, user, label_id)
    db.commit()
    return Response(status_code=204)


@router.post("/tasks/{task_id}/labels", status_code=201)
def attach_label(task_id: int, body: AttachIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    labels_service.attach(db, user, task_id, body.label_id)
    db.commit()
    return {"task_id": task_id, "label_id": body.label_id}


@router.delete("/tasks/{task_id}/labels/{label_id}", status_code=204)
def detach_label(task_id: int, label_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    labels_service.detach(db, user, task_id, label_id)
    db.commit()
    return Response(status_code=204)
