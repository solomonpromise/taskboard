"""Task behaviour, from the acceptance criteria in the brief (book Chapters 3 and 28)."""
from datetime import date, timedelta

from sqlalchemy import select

from app import models


def future(days):
    return (date.today() + timedelta(days=days + 1)).isoformat()


def test_create_task_and_see_it_in_my_list(sign_up):
    amara = sign_up("Amara")
    r = amara.post("/v1/tasks", json={"title": "Submit invoice", "due_date": future(5)})
    assert r.status_code == 201
    assert r.json()["title"] == "Submit invoice" and r.json()["is_done"] is False
    titles = [t["title"] for t in amara.get("/v1/tasks").json()["items"]]
    assert titles == ["Submit invoice"]


def test_rejects_empty_title_and_stores_nothing(sign_up, db_session_factory):
    amara = sign_up("Amara")
    r = amara.post("/v1/tasks", json={"title": "   "})
    assert r.status_code == 400 and r.json()["error"]["message"] == "Please add a title."
    assert db_session_factory().scalar(select(models.Task)) is None


def test_rejects_titles_over_200_characters(sign_up):
    amara = sign_up("Amara")
    assert amara.post("/v1/tasks", json={"title": "x" * 201}).status_code == 400
    assert amara.post("/v1/tasks", json={"title": "x" * 200}).status_code == 201


def test_rejects_due_dates_in_the_past(sign_up):
    amara = sign_up("Amara")
    yesterday = (date.today() - timedelta(days=2)).isoformat()
    r = amara.post("/v1/tasks", json={"title": "Late", "due_date": yesterday})
    assert r.status_code == 400 and r.json()["error"]["code"] == "invalid_due_date"


def test_list_is_soonest_first_with_undated_last(sign_up):
    amara = sign_up("Amara")
    amara.post("/v1/tasks", json={"title": "No date"})
    amara.post("/v1/tasks", json={"title": "Later", "due_date": future(10)})
    amara.post("/v1/tasks", json={"title": "Sooner", "due_date": future(2)})
    titles = [t["title"] for t in amara.get("/v1/tasks").json()["items"]]
    assert titles == ["Sooner", "Later", "No date"]


def test_marking_done_moves_task_to_completed_list(sign_up):
    amara = sign_up("Amara")
    task = amara.post("/v1/tasks", json={"title": "Call the bank"}).json()
    r = amara.patch(f"/v1/tasks/{task['id']}", json={"is_done": True})
    assert r.status_code == 200 and r.json()["completed_at"] is not None
    assert amara.get("/v1/tasks").json()["items"] == []
    assert [t["title"] for t in amara.get("/v1/tasks?status=done").json()["items"]] == ["Call the bank"]


def test_overdue_flag_uses_the_users_today(sign_up, db_session_factory):
    amara = sign_up("Amara")
    db = db_session_factory()
    db.add(models.Task(owner_id=amara.user["id"], title="Pay electricity bill",
                       due_date=date.today() - timedelta(days=3)))
    db.commit()
    [task] = amara.get("/v1/tasks").json()["items"]
    assert task["is_overdue"] is True


def test_double_submit_with_same_idempotency_key_creates_one_task(sign_up):
    amara = sign_up("Amara")
    headers = {"Idempotency-Key": "7c1e-test"}
    first = amara.post("/v1/tasks", json={"title": "Submit invoice"}, headers=headers)
    second = amara.post("/v1/tasks", json={"title": "Submit invoice"}, headers=headers)
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert len(amara.get("/v1/tasks").json()["items"]) == 1


def test_list_is_paged(sign_up):
    amara = sign_up("Amara")
    for i in range(3):
        amara.post("/v1/tasks", json={"title": f"Task {i}"})
    page1 = amara.get("/v1/tasks?limit=2").json()
    page2 = amara.get(f"/v1/tasks?limit=2&cursor={page1['next_cursor']}").json()
    assert len(page1["items"]) == 2 and len(page2["items"]) == 1 and page2["next_cursor"] is None


def test_delete_task(sign_up):
    amara = sign_up("Amara")
    task = amara.post("/v1/tasks", json={"title": "Temporary"}).json()
    assert amara.delete(f"/v1/tasks/{task['id']}").status_code == 204
    assert amara.get(f"/v1/tasks/{task['id']}").status_code == 404
