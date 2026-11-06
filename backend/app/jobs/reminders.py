"""Morning reminders (book Chapters 7, 19 and 22).

Run every 15 minutes (cron, or your platform's scheduler):
    python -m app.jobs.reminders

1. queue_due_reminders: for users whose local time is 07:00-07:14, queue ONE email listing tasks
   due today (their local date). The unique dedupe key makes repeats harmless.
2. send_outbox: send queued emails through the adapter; failures are retried on the next run.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import OutboxMessage, Task, User
from ..notifications.email import EmailError, send_email

SEND_HOUR = 7
WINDOW_MINUTES = 15
MAX_ATTEMPTS = 5


def queue_due_reminders(db: Session, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    queued = 0
    for user in db.scalars(select(User)):
        local = now.astimezone(ZoneInfo(user.time_zone))
        if not (local.hour == SEND_HOUR and local.minute < WINDOW_MINUTES):
            continue
        due = list(db.scalars(select(Task).where(
            Task.owner_id == user.id, Task.is_done.is_(False), Task.due_date == local.date()
        ).order_by(Task.id)))
        if not due:
            continue
        key = f"reminder:{user.id}:{local.date().isoformat()}"
        if db.scalar(select(OutboxMessage.id).where(OutboxMessage.dedupe_key == key)):
            continue
        lines = "\n".join(f"- {t.title}" for t in due)
        db.add(OutboxMessage(dedupe_key=key, recipient=user.email,
                             subject=f"Due today: {len(due)} task{'s' if len(due) != 1 else ''}",
                             body=f"Hi {user.name},\n\nThese tasks are due today:\n{lines}\n\n- Taskboard"))
        try:
            db.commit()
            queued += 1
        except IntegrityError:  # another run queued it first; that's fine
            db.rollback()
    return queued


def send_outbox(db: Session, mode: str | None = None) -> int:
    sent = 0
    pending = db.scalars(select(OutboxMessage).where(
        OutboxMessage.sent_at.is_(None), OutboxMessage.attempts < MAX_ATTEMPTS
    ).order_by(OutboxMessage.id))
    for message in list(pending):
        try:
            send_email(message.recipient, message.subject, message.body, mode=mode)
            message.sent_at = datetime.now(timezone.utc)
            sent += 1
        except EmailError as exc:
            message.attempts += 1
            message.last_error = str(exc)[:300]
        db.commit()
    return sent


if __name__ == "__main__":
    from ..db import SessionLocal
    from ..logging_setup import configure_logging

    configure_logging()
    with SessionLocal() as session:
        print(f"queued {queue_due_reminders(session)}; sent {send_outbox(session)}")
