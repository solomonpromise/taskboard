# Where each chapter lives

| Chapter | In this repository |
|---|---|
| 1 What software and applications are | The whole app: `frontend/` (interface), `backend/app/services` (logic), the database (data) |
| 2 Types of applications | A hosted web app; `backend/app/jobs/` is the no-screen scheduled job |
| 3 Requirements | [`docs/brief.md`](brief.md): problem, users, scope, acceptance criteria |
| 4 Lifecycle | `git log`: each commit is one planned, tested, released increment |
| 5 Programming foundations | `backend/app/services/dates.py` (`is_overdue`), `services/tasks.py` |
| 6 Frontend | `frontend/src/pages/TasksPage.tsx` (four screen states), `components/TaskRow.tsx`, `TaskForm.tsx` |
| 7 Backend | `backend/app/routes/` → `services/` → `repositories/`; `deps.py` identifies the user |
| 8 HTTP and APIs | [`docs/api.md`](api.md), `frontend/src/api/client.ts` (timeouts, errors) |
| 9 Databases | `backend/app/models.py`, `db.py` (SQLite locally, PostgreSQL via Docker) |
| 10 Data modelling | `models.py`, `backend/migrations/versions/`, constraints and the owner index |
| 11 Authentication | `security.py` (Argon2, NIST 800-63B-4 rules, cookies, guess limiting), `deps.py` (CSRF), `tests/test_auth.py`, `tests/test_permissions.py` |
| 12 Following an action | [`docs/architecture.md`](architecture.md): component and sequence diagrams |
| 13 Project structure | This repository's layout (see README) |
| 14 Repositories | This Git repository and its history |
| 15 Git | Small commits; `.github/pull_request_template.md` |
| 16 Environments and dependencies | `Makefile`, `requirements*.txt`, `package-lock.json`, `.nvmrc`, `.python-version` |
| 17 Configuration and secrets | `backend/.env.example`, `backend/app/config.py`, `.gitignore` |
| 18 Documentation | `README.md`, `AGENTS.md`, `docs/`, `docs/decisions/` |
| 19 Requirements to design | [`docs/design.md`](design.md) |
| 20 Architecture | Modular monolith with layers; [ADR 002](decisions/002-modular-monolith.md) |
| 21 Choosing technology | [ADR 003](decisions/003-fastapi.md), [ADR 004](decisions/004-database.md) |
| 22 Data and integrations | Idempotency keys (`routes/tasks.py`), email adapter + outbox (`notifications/`, `jobs/`) |
| 23 Quality and change | Trust boundaries in `docs/architecture.md`, [`docs/debt.md`](debt.md) |
| 24–25 AI tools and tasks | `AGENTS.md`, [`docs/templates.md`](templates.md) |
| 26 Increments | The commit history: skeleton → data → auth → tasks → labels → reminders → frontend |
| 27 Review | Pull request template checklist |
| 28 Testing | `tests/` (unit, API, permissions, migrations), `frontend/src/lib/dates.test.ts` |
| 29 Debugging | The time-zone rule and its tests (`tests/test_dates.py`), structured logs with request IDs |
| 30 Deployment | `Dockerfile`, `docker-compose.yml`, [`docs/runbook.md`](runbook.md) |
| 31 Releasing | `.github/workflows/ci.yml`, `scripts/smoke_test.py`, migrations run before start |
| 32 Observing | `/health`, `logging_setup.py` (JSON logs, request IDs, no secrets) |
| 33 Recovery | `scripts/backup.sh`, restore steps in [`docs/runbook.md`](runbook.md) |
| 34 Maintenance | [`docs/maintenance.md`](maintenance.md) |
