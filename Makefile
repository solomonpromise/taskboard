# Taskboard commands (book Chapter 16). Run `make help` to list them.
PY := backend/.venv/bin/python
.DEFAULT_GOAL := help

help: ## List commands
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

install: ## Install backend and frontend dependencies
	test -d backend/.venv || python3 -m venv backend/.venv
	$(PY) -m pip install -q -r backend/requirements-dev.txt
	cd frontend && npm ci
	test -f backend/.env || cp backend/.env.example backend/.env

migrate: ## Apply database migrations
	cd backend && .venv/bin/alembic upgrade head

dev: ## Run backend (:8000) and frontend (:5173) with auto-reload
	./scripts/dev.sh

test: ## Run all tests
	$(PY) -m pytest
	cd frontend && npm test

build: ## Build the frontend for production (served by the backend)
	cd frontend && npm run build

start: build ## Run the production-style single server on :8000
	cd backend && .venv/bin/uvicorn app.main:app --port 8000

smoke: ## Smoke-test a running app (URL=http://localhost:8000)
	$(PY) scripts/smoke_test.py $(or $(URL),http://localhost:8000)

reminders: ## Queue and send due-today reminder emails once
	cd backend && .venv/bin/python -m app.jobs.reminders

backup: ## Back up the database to backups/
	./scripts/backup.sh

.PHONY: help install migrate dev test build start smoke reminders backup
