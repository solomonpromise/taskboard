# Instructions for AI coding tools

Taskboard is the companion application for the book *Software Foundations for Vibe Coders*.
Read this file and `docs/design.md` before changing anything.

## Stack
- Backend: Python 3.12+, FastAPI, SQLAlchemy 2, Alembic migrations (`backend/`)
- Frontend: React + TypeScript, built with Vite (`frontend/`)
- Database: SQLite locally by default; PostgreSQL via Docker Compose or in production
- Do not add new frameworks, databases or dependencies without asking.

## Commands
- `make install` · `make migrate` · `make dev` · `make test` · `make build`

## Rules that must always hold
- Every query on user data filters by `owner_id` taken from the session, never from the request.
- Layers: routes (HTTP only) → services (rules) → repositories (the only place with queries).
- Validate all input in the backend; the frontend checks are for convenience only.
- Due dates are calendar dates. Timestamps are UTC. "Today" is the user's local date (`users.time_zone`).
- Errors use one format: `{"error": {"code": "...", "message": "..."}}`.
- Never commit `.env`, secrets, `node_modules/`, `.venv/`, `dist/` or database files.
- Never log passwords, session tokens, CSRF tokens or request bodies.
- Every change: small, with tests, all tests passing (`make test`), docs updated if behaviour changed.
