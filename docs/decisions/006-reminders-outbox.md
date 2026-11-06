# ADR 006: Reminder emails through an outbox and an email adapter
Date: 2026-11-05 · Status: Accepted

**Context.** Email is a utility; providers fail sometimes; reminders must never be sent twice.
**Decision.** A job queues one reminder per user per local day in an `outbox` table with a unique
key; a sender delivers through `notifications/email.py` and retries failures. Console mode locally.
**Consequences.** No lost or duplicated reminders; switching provider touches one file.
**Revisit if.** Volume needs a real queue, or we add other notification channels.
