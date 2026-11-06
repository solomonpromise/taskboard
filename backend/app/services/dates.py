"""Date rules, used everywhere (book Chapter 10):

- A due date is a calendar date with no time of day.
- Events (created_at, completed_at) are UTC timestamps.
- "Today" is the user's local date, from users.time_zone, never the server's.
"""
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo


def user_today(time_zone: str, now: datetime | None = None) -> date:
    now = now or datetime.now(timezone.utc)
    return now.astimezone(ZoneInfo(time_zone)).date()


def is_overdue(due_date: date | None, today: date) -> bool:
    """True if the due date is before today (the user's local date). Undated tasks are never overdue."""
    if due_date is None:
        return False
    return due_date < today
