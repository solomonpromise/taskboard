"""Test setup: a fresh in-memory SQLite database for every test, and helpers for signed-in users."""
import sys
from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app import db as db_module  # noqa: E402
from app import models  # noqa: E402,F401  (registers tables)
from app import security  # noqa: E402
from app.main import app  # noqa: E402

PASSWORD = "a long and unusual pass phrase"


@pytest.fixture(autouse=True)
def _reset_limiter():
    security.sign_in_limiter._failures.clear()
    yield


@pytest.fixture()
def db_session_factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    db_module.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def make_client(db_session_factory):
    """Create independent browsers (each with its own cookies) against the same database."""
    def _get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[db_module.get_db] = _get_db
    clients = []

    def _make():
        c = TestClient(app)
        clients.append(c)
        return c

    yield _make
    for c in clients:
        c.close()
    app.dependency_overrides.clear()


@pytest.fixture()
def client(make_client):
    return make_client()


class SignedInUser:
    """A signed-in browser that sends the CSRF header automatically, like the real frontend."""

    def __init__(self, client: TestClient, user: dict):
        self.client, self.user = client, user

    def _headers(self, extra=None):
        headers = {"X-CSRF-Token": self.client.cookies.get(security.CSRF_COOKIE, "")}
        headers.update(extra or {})
        return headers

    def get(self, url, **kw):
        return self.client.get(url, **kw)

    def post(self, url, json=None, headers=None):
        return self.client.post(url, json=json, headers=self._headers(headers))

    def patch(self, url, json=None):
        return self.client.patch(url, json=json, headers=self._headers())

    def delete(self, url):
        return self.client.delete(url, headers=self._headers())


@pytest.fixture()
def sign_up(make_client):
    def _sign_up(name="Amara", email=None, time_zone="UTC"):
        c = make_client()
        email = email or f"{name.lower()}@example.com"
        r = c.post("/v1/auth/sign-up", json={"name": name, "email": email, "password": PASSWORD,
                                             "time_zone": time_zone})
        assert r.status_code == 201, r.text
        return SignedInUser(c, r.json())
    return _sign_up
