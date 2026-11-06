"""Two-account permission tests (book Chapter 11 walkthrough). Nobody can see or change another user's tasks."""


def test_cannot_read_another_users_task(sign_up):
    amara, tunde = sign_up("Amara"), sign_up("Tunde")
    task = amara.post("/v1/tasks", json={"title": "Submit invoice"}).json()
    assert tunde.get(f"/v1/tasks/{task['id']}").status_code == 404


def test_cannot_change_or_delete_another_users_task(sign_up):
    amara, tunde = sign_up("Amara"), sign_up("Tunde")
    task = amara.post("/v1/tasks", json={"title": "Submit invoice"}).json()
    assert tunde.patch(f"/v1/tasks/{task['id']}", json={"is_done": True}).status_code == 404
    assert tunde.delete(f"/v1/tasks/{task['id']}").status_code == 404
    unchanged = amara.get(f"/v1/tasks/{task['id']}").json()
    assert unchanged["is_done"] is False


def test_list_only_shows_my_tasks(sign_up):
    amara, tunde = sign_up("Amara"), sign_up("Tunde")
    amara.post("/v1/tasks", json={"title": "Amara's task"})
    tunde.post("/v1/tasks", json={"title": "Tunde's task"})
    assert [t["title"] for t in tunde.get("/v1/tasks").json()["items"]] == ["Tunde's task"]


def test_signed_out_users_get_401_on_every_task_route(client):
    assert client.get("/v1/tasks").status_code == 401
    assert client.post("/v1/tasks", json={"title": "x"}).status_code == 401
    assert client.patch("/v1/tasks/1", json={"is_done": True}).status_code == 401
    assert client.delete("/v1/tasks/1").status_code == 401


def test_owner_cannot_be_set_from_the_request_body(sign_up):
    amara, tunde = sign_up("Amara"), sign_up("Tunde")
    task = tunde.post("/v1/tasks", json={"title": "Sneaky", "owner_id": amara.user["id"]}).json()
    assert amara.get(f"/v1/tasks/{task['id']}").status_code == 404
    assert tunde.get(f"/v1/tasks/{task['id']}").status_code == 200
