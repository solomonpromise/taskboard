"""Labels (book Chapters 25-28), including the 'attach twice is harmless' criterion."""
from sqlalchemy import event


def test_attach_label_and_see_it_on_the_task(sign_up):
    amara = sign_up("Amara")
    task = amara.post("/v1/tasks", json={"title": "Submit invoice"}).json()
    label = amara.post("/v1/labels", json={"name": "work"}).json()
    assert amara.post(f"/v1/tasks/{task['id']}/labels", json={"label_id": label["id"]}).status_code == 201
    [listed] = amara.get("/v1/tasks").json()["items"]
    assert listed["labels"] == [{"id": label["id"], "name": "work"}]


def test_attach_twice_is_harmless(sign_up):
    amara = sign_up("Amara")
    task = amara.post("/v1/tasks", json={"title": "Submit invoice"}).json()
    label = amara.post("/v1/labels", json={"name": "work"}).json()
    for _ in range(2):
        assert amara.post(f"/v1/tasks/{task['id']}/labels", json={"label_id": label["id"]}).status_code == 201
    assert len(amara.get(f"/v1/tasks/{task['id']}").json()["labels"]) == 1


def test_cannot_use_another_users_task_or_label(sign_up):
    amara, tunde = sign_up("Amara"), sign_up("Tunde")
    amaras_task = amara.post("/v1/tasks", json={"title": "Amara's"}).json()
    amaras_label = amara.post("/v1/labels", json={"name": "private"}).json()
    tundes_task = tunde.post("/v1/tasks", json={"title": "Tunde's"}).json()
    assert tunde.post(f"/v1/tasks/{amaras_task['id']}/labels", json={"label_id": amaras_label["id"]}).status_code == 404
    assert tunde.post(f"/v1/tasks/{tundes_task['id']}/labels", json={"label_id": amaras_label["id"]}).status_code == 404
    assert tunde.get("/v1/labels").json()["items"] == []


def test_task_list_loads_labels_in_one_query(sign_up, db_session_factory):
    amara = sign_up("Amara")
    label = amara.post("/v1/labels", json={"name": "work"}).json()
    for i in range(5):
        task = amara.post("/v1/tasks", json={"title": f"Task {i}"}).json()
        amara.post(f"/v1/tasks/{task['id']}/labels", json={"label_id": label["id"]})

    engine = db_session_factory.kw["bind"]
    statements = []
    listener = lambda *args: statements.append(args[2])  # noqa: E731
    event.listen(engine, "before_cursor_execute", listener)
    amara.get("/v1/tasks")
    event.remove(engine, "before_cursor_execute", listener)
    label_queries = [s for s in statements if "task_labels" in s]
    assert len(label_queries) == 1
