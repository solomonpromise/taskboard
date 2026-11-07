# Taskboard design · v1

## Goals and quality requirements
- Scope: the first useful version in [`brief.md`](brief.md).
- Performance: task list in under 1 s for 95% of requests, for users with up to 1,000 tasks.
- Availability: 99.5% per month. Security: no user can read or change another user's data.
- Accessibility: WCAG 2.2 AA; every journey works by keyboard.

## Constraints and assumptions
- Up to 10,000 users in the first year; under 20 requests per second at peak.
- Budget under $50/month; one builder using AI tools.
- Assume: no offline use, no teams in v1.
- Dates: due dates are calendar dates; timestamps are UTC; "today" is the user's local date.

## Components and responsibilities
- **Web app** (React): interface and temporary state only. Never the source of truth.
- **API** (FastAPI): all rules, authentication and authorisation; the only database client.
- **Database** (SQLite locally, PostgreSQL in production): the source of truth.
- **Reminder job**: queues due-today emails in an outbox; sends through the email adapter.
- **Email adapter**: console locally; SMTP provider in production.

See [`architecture.md`](architecture.md) for diagrams and [`decisions/`](decisions/) for the reasons.

## Quality tactics (book Chapter 23)

| Quality | Tactic |
|---|---|
| Security | Owner filter in every query; deny by default; sessions in HttpOnly cookies plus CSRF tokens; slow password hashes; sign-in guess limiting |
| Reliability | Database constraints; idempotency keys on task creation; outbox for reminder emails; `/health` checks the database |
| Performance | Index on `tasks(owner_id, is_done, due_date)`; paginated lists; labels loaded in one query |
| Privacy | Collect only name, email, time zone and tasks; no personal data in logs; account export and deletion before public launch (`debt.md`) |
| Accessibility | Real buttons and labels; visible focus; overdue shown with text, not colour alone |
| Maintainability | Routes → services → repositories layers; ADRs; tests for every acceptance criterion |

## One-way doors

The data model and the API contract are expensive to change once clients and real data depend on them.
Changing either needs a new ADR, and breaking API changes go through a new version (`/v2/`).

## Out of scope for v1
- Password reset and email verification (see [`brief.md`](brief.md)).

## Open questions
- Retention of deleted tasks.
