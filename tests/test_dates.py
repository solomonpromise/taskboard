"""Unit tests for the date rules (book Chapters 5 and 10, and bug #31 in Chapter 29)."""
from datetime import date, datetime, timezone

from app.services.dates import is_overdue, user_today


def test_undated_tasks_are_never_overdue():
    assert is_overdue(None, date(2026, 11, 12)) is False


def test_due_today_is_not_overdue_but_yesterday_is():
    today = date(2026, 11, 12)
    assert is_overdue(date(2026, 11, 12), today) is False
    assert is_overdue(date(2026, 11, 11), today) is True


def test_today_is_the_users_local_date_not_the_servers():
    # 01:00 UTC on 13 Nov is still the evening of 12 Nov in New York (UTC-5).
    now = datetime(2026, 11, 13, 1, 0, tzinfo=timezone.utc)
    assert user_today("UTC", now) == date(2026, 11, 13)
    assert user_today("America/New_York", now) == date(2026, 11, 12)
    # A task due on 12 Nov is due today for the New York user, not overdue (the Chapter 29 bug).
    assert is_overdue(date(2026, 11, 12), user_today("America/New_York", now)) is False
