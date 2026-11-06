# ADR 003: FastAPI for the backend
Date: 2026-11-05 · Status: Accepted

**Context.** JSON API, relational data, readable code for review, strong AI-tool support.
**Options.** FastAPI (Python) 51 · Express (Node) 49 · Rails (Ruby) 39 (weighted matrix, book Fig 21.1).
**Decision.** FastAPI, with SQLAlchemy and Alembic. Familiarity decided a close call.
**Consequences.** Typed request models and automatic API docs; two languages across the stack.
**Revisit if.** The team becomes Node-focused or needs heavy real-time features.
