"""Sign-up, sign-in and sign-out routes. HTTP only; rules live in services/auth.py."""
from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from .. import security
from ..db import get_db
from ..deps import current_user
from ..models import User
from ..repositories import users as users_repo
from ..services import auth as auth_service

router = APIRouter(prefix="/v1")


class SignUpIn(BaseModel):
    name: str = Field(max_length=100)
    email: EmailStr
    password: str = Field(max_length=security.MAX_PASSWORD_LENGTH + 1)
    time_zone: str = "UTC"


class SignInIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=security.MAX_PASSWORD_LENGTH + 1)


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    time_zone: str


def _user_out(user: User) -> UserOut:
    return UserOut(id=user.id, name=user.name, email=user.email, time_zone=user.time_zone)


@router.post("/auth/sign-up", status_code=201, response_model=UserOut)
def sign_up(body: SignUpIn, response: Response, db: Session = Depends(get_db)):
    user = auth_service.sign_up(db, name=body.name, email=body.email, password=body.password,
                                time_zone=body.time_zone)
    session_token, csrf_token = auth_service.start_session(db, user)
    db.commit()
    security.set_session_cookies(response, session_token, csrf_token)
    return _user_out(user)


@router.post("/auth/sign-in", response_model=UserOut)
def sign_in(body: SignInIn, response: Response, db: Session = Depends(get_db)):
    user = auth_service.sign_in(db, email=body.email, password=body.password)
    session_token, csrf_token = auth_service.start_session(db, user)
    db.commit()
    security.set_session_cookies(response, session_token, csrf_token)
    return _user_out(user)


@router.post("/auth/sign-out", status_code=204)
def sign_out(request: Request, response: Response, db: Session = Depends(get_db),
             _user: User = Depends(current_user)):
    users_repo.delete_session(db, security.hash_token(request.cookies[security.SESSION_COOKIE]))
    db.commit()
    security.clear_session_cookies(response)
    response.status_code = 204
    return response


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return _user_out(user)
