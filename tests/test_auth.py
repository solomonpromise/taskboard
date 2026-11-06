"""Authentication behaviour (book Chapter 11)."""
from sqlalchemy import select

from app import models
from conftest import PASSWORD


def test_sign_up_sets_secure_session_cookies(client):
    r = client.post("/v1/auth/sign-up", json={"name": "Amara", "email": "amara@example.com",
                                              "password": PASSWORD, "time_zone": "Europe/London"})
    assert r.status_code == 201
    cookies = r.headers.get_list("set-cookie")
    session_cookie = next(c for c in cookies if c.startswith("session="))
    assert "HttpOnly" in session_cookie and "SameSite=lax" in session_cookie
    csrf_cookie = next(c for c in cookies if c.startswith("csrf_token="))
    assert "HttpOnly" not in csrf_cookie  # the frontend must be able to read it
    assert r.json()["time_zone"] == "Europe/London"


def test_password_is_stored_only_as_a_hash(client, db_session_factory):
    client.post("/v1/auth/sign-up", json={"name": "Amara", "email": "amara@example.com", "password": PASSWORD})
    user = db_session_factory().scalar(select(models.User))
    assert user.password_hash != PASSWORD and user.password_hash.startswith("$argon2")


def test_short_password_rejected_with_helpful_message(client):
    r = client.post("/v1/auth/sign-up", json={"name": "A", "email": "a@example.com", "password": "short"})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "weak_password"


def test_common_password_rejected(client):
    r = client.post("/v1/auth/sign-up", json={"name": "A", "email": "a@example.com",
                                              "password": "correcthorsebatterystaple"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "weak_password"


def test_unknown_time_zone_rejected(client):
    r = client.post("/v1/auth/sign-up", json={"name": "A", "email": "a@example.com", "password": PASSWORD,
                                              "time_zone": "Mars/Olympus"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "invalid_time_zone"


def test_sign_in_error_does_not_reveal_which_part_was_wrong(sign_up, make_client):
    sign_up("Amara")
    c = make_client()
    wrong_password = c.post("/v1/auth/sign-in", json={"email": "amara@example.com", "password": "x" * 20})
    unknown_email = c.post("/v1/auth/sign-in", json={"email": "nobody@example.com", "password": "x" * 20})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_repeated_failures_are_slowed_down(sign_up, make_client):
    sign_up("Amara")
    c = make_client()
    for _ in range(5):
        c.post("/v1/auth/sign-in", json={"email": "amara@example.com", "password": "y" * 20})
    r = c.post("/v1/auth/sign-in", json={"email": "amara@example.com", "password": PASSWORD})
    assert r.status_code == 429


def test_me_requires_sign_in(client):
    r = client.get("/v1/me")
    assert r.status_code == 401 and r.json()["error"]["code"] == "not_signed_in"


def test_changes_without_csrf_token_are_rejected(sign_up):
    amara = sign_up("Amara")
    r = amara.client.post("/v1/auth/sign-out")  # no X-CSRF-Token header
    assert r.status_code == 403 and r.json()["error"]["code"] == "csrf_failed"


def test_sign_out_ends_the_session(sign_up):
    amara = sign_up("Amara")
    assert amara.post("/v1/auth/sign-out").status_code == 204
    assert amara.get("/v1/me").status_code == 401


def test_password_containing_email_name_rejected(client):
    r = client.post("/v1/auth/sign-up", json={"name": "Amara", "email": "amaraokafor@example.com",
                                              "password": "amaraokafor is my password"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "weak_password"
