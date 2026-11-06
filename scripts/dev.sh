#!/bin/sh
# Start the backend and frontend together for local development; Ctrl+C stops both.
set -e
cd "$(dirname "$0")/.."
(cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000) &
BACKEND=$!
trap 'kill $BACKEND 2>/dev/null' EXIT INT TERM
cd frontend && npm run dev
