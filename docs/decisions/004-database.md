# ADR 004: SQLite locally, PostgreSQL in production
Date: 2026-11-05 · Status: Accepted

**Context.** Strongly related data (users, tasks, labels), transactions, owner filters; readers
need a free local route without Docker.
**Options.** PostgreSQL everywhere; SQLite everywhere; MongoDB.
**Decision.** SQLAlchemy models and Alembic migrations that run on both: SQLite by default for local
work and tests, PostgreSQL via Docker Compose and in production. CI applies every migration to
PostgreSQL.
**Consequences.** Zero-setup start; small dialect differences are caught by CI.
**Revisit if.** We need PostgreSQL-only features (full-text search, JSON queries).
