"""Reminder job: one email per user per local day, sent through the outbox (book Chapters 7 and 22)."""
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import select

from app import models
from app.jobs import reminders
from app.notifications import email


@pytest.fixture()
def db(db_session_factory):
    session = db_session_factory()
    user = models.User(name="Amara", email="amara@example.com", password_hash="x", time_zone="America/New_York")
    session.add(user)
    session.flush()
    session.add_all([
        models.Task(owner_id=user.id, title="Submit invoice", due_date=date(2026, 11, 12)),
        models.Task(owner_id=user.id, title="Already done", due_date=date(2026, 11, 12), is_done=True),
        models.Task(owner_id=user.id, title="Next week", due_date=date(2026, 11, 19)),
    ])
    session.commit()
    email.sent_in_memory.clear()
    return session


SEVEN_AM_NEW_YORK = datetime(2026, 11, 12, 12, 5, tzinfo=timezone.utc)  # 07:05 in New York (UTC-5)


def test_queues_one_reminder_at_seven_local_time(db):
    assert reminders.queue_due_reminders(db, SEVEN_AM_NEW_YORK) == 1
    [message] = db.scalars(select(models.OutboxMessage))
    assert "Submit invoice" in message.body
    assert "Already done" not in message.body and "Next week" not in message.body


def test_running_twice_does_not_queue_twice(db):
    reminders.queue_due_reminders(db, SEVEN_AM_NEW_YORK)
    assert reminders.queue_due_reminders(db, SEVEN_AM_NEW_YORK) == 0
    assert len(list(db.scalars(select(models.OutboxMessage)))) == 1


def test_nothing_outside_the_morning_window(db):
    nine_am = datetime(2026, 11, 12, 14, 0, tzinfo=timezone.utc)
    assert reminders.queue_due_reminders(db, nine_am) == 0


def test_send_outbox_sends_once_and_marks_sent(db):
    reminders.queue_due_reminders(db, SEVEN_AM_NEW_YORK)
    assert reminders.send_outbox(db, mode="memory") == 1
    assert reminders.send_outbox(db, mode="memory") == 0
    assert email.sent_in_memory[0]["to"] == "amara@example.com"


def test_failed_sends_are_retried_later(db, monkeypatch):
    reminders.queue_due_reminders(db, SEVEN_AM_NEW_YORK)

    def failing(*_args, **_kwargs):
        raise email.EmailError("provider unavailable")

    monkeypatch.setattr(reminders, "send_email", failing)
    assert reminders.send_outbox(db) == 0
    [message] = db.scalars(select(models.OutboxMessage))
    assert message.attempts == 1 and message.sent_at is None
    monkeypatch.undo()
    assert reminders.send_outbox(db, mode="memory") == 1
