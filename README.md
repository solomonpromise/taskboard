# Taskboard

A simple, reliable task tracker: capture tasks, set due dates, see what's next.

Taskboard is the companion application for the book **Software Foundations for Vibe Coders**
by Solomon Promise. Every idea the book teaches with Taskboard (the data model, the API, sign-in
and permissions, tests, the deployment pipeline, backups) exists here as real, working code.
[`docs/book-map.md`](docs/book-map.md) shows where each chapter lives in this repository.

## Quick start (free, local: no accounts, no Docker)

Needs Python 3.12+, Node.js 20+ and Git.

```bash
git clone <this repository> taskboard && cd taskboard
make install     # backend virtualenv + packages, frontend packages, creates backend/.env
make migrate     # creates the local SQLite database
make dev         # backend on :8000, frontend on http://localhost:5173
```

Open http://localhost:5173, create an account and add a task. Reminder emails are printed to the
terminal (`EMAIL_MODE=console`), so nothing is ever sent.

To run it the way production does (one server, built frontend): `make start`, then open
http://localhost:8000.

### With PostgreSQL (optional, needs Docker)

```bash
docker compose up --build    # PostgreSQL + the app on http://localhost:8000
```

## Commands

| Command | What it does |
|---|---|
| `make install` | Install dependencies and create `backend/.env` from `.env.example` |
| `make migrate` | Apply database migrations |
| `make dev` | Run backend and frontend with auto-reload |
| `make test` | Run all backend and frontend tests |
| `make build` / `make start` | Build the frontend / run the production-style server |
| `make smoke URL=…` | Smoke-test a running copy (local or staging) |
| `make reminders` | Queue and send today's reminder emails once |
| `make backup` | Back up the database to `backups/` |

## Project structure

```
backend/app/        FastAPI application
  routes/           HTTP only: parse requests, call services, shape responses
  services/         business rules (tasks, labels, auth, dates)
  repositories/     the only place with database queries; every query filters by owner
  notifications/    email adapter (console, SMTP)
  jobs/             scheduled reminder job (outbox)
backend/migrations/ versioned database changes (Alembic)
frontend/src/       React + TypeScript: pages, components, API client
tests/              backend tests: unit, API, permissions, migrations, reminders
docs/               brief, design, API contract, architecture, decisions, runbook
scripts/            dev server, smoke test, backup
```

## Configuration

All settings come from environment variables; every one is described in
[`backend/.env.example`](backend/.env.example). Never commit `backend/.env`.

## Conventions

- Layers: routes → services → repositories. Business rules never live in routes or components.
- Every query on user data filters by `owner_id` from the session. Others' records return 404.
- Due dates are calendar dates; timestamps are UTC; "today" is the user's local date.
- One error format: `{"error": {"code": "...", "message": "..."}}`.
- Small changes, each with tests, through a pull request (see the template).

## Working with AI tools

Read [`AGENTS.md`](AGENTS.md) first; point your AI tool at it and at [`docs/design.md`](docs/design.md)
at the start of every task. The task format from Chapter 25 is in
[`docs/templates.md`](docs/templates.md).

## Deploying and operating

See [`docs/runbook.md`](docs/runbook.md) (deploy, roll back, restore, rotate secrets) and
[`docs/maintenance.md`](docs/maintenance.md) (monitoring, updates, backups, routine).

## Licence

MIT. See [`LICENSE`](LICENSE).
