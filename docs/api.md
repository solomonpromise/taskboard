# API contract · v1

All endpoints are under `/v1`, return JSON, and use one error format:
`{"error": {"code": "invalid_title", "message": "Please add a title."}}`.
Requests that change data must send `X-CSRF-Token` (the value of the `csrf_token` cookie).

| Method | Path | Who | Success | Notes |
|---|---|---|---|---|
| POST | `/v1/auth/sign-up` | anyone | 201 user | password ≥ 15 chars; sets session cookies |
| POST | `/v1/auth/sign-in` | anyone | 200 user | generic 401 on failure; 429 after 5 failures |
| POST | `/v1/auth/sign-out` | signed in | 204 | |
| GET | `/v1/me` | signed in | 200 user | |
| GET | `/v1/tasks?status=open\|done&limit=50&cursor=0` | signed in | 200 page | soonest first, undated last; `next_cursor` |
| GET | `/v1/tasks/{id}` | owner | 200 task | 404 if not yours |
| POST | `/v1/tasks` | signed in | 201 task | optional `Idempotency-Key` header |
| PATCH | `/v1/tasks/{id}` | owner | 200 task | any of `title`, `due_date`, `is_done` |
| DELETE | `/v1/tasks/{id}` | owner | 204 | |
| GET / POST | `/v1/labels` | signed in | 200 / 201 | names unique per user |
| DELETE | `/v1/labels/{id}` | owner | 204 | |
| POST | `/v1/tasks/{id}/labels` | owner | 201 | `{"label_id": n}`; attaching twice is harmless |
| DELETE | `/v1/tasks/{id}/labels/{label_id}` | owner | 204 | |
| GET | `/health` | anyone | 200 | 503 if the database is unreachable |

Task shape:

```json
{ "id": 42, "title": "Submit invoice", "due_date": "2026-11-12", "is_done": false,
  "is_overdue": false, "created_at": "2026-11-05T09:12:00+00:00", "completed_at": null,
  "labels": [{ "id": 1, "name": "work" }] }
```

Interactive documentation is generated at `/docs` while the backend is running.
