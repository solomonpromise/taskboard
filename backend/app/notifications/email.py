"""Email adapter (book Chapter 22): the rest of the code calls send_email() and never sees the provider.

EMAIL_MODE=console prints emails as log lines (free, local).
EMAIL_MODE=smtp sends through SMTP_URL, e.g. smtp://user:password@smtp.example.com:587
EMAIL_MODE=memory keeps them in a list (used by tests).
"""
import logging
import smtplib
from email.message import EmailMessage
from urllib.parse import unquote, urlparse

from ..config import settings

log = logging.getLogger("taskboard")
sent_in_memory: list[dict] = []


class EmailError(Exception):
    pass


def send_email(to: str, subject: str, body: str, mode: str | None = None) -> None:
    mode = mode or settings.email_mode
    if mode == "memory":
        sent_in_memory.append({"to": to, "subject": subject, "body": body})
    elif mode == "console":
        log.info("email (console mode, not sent)", extra={"fields": {"subject": subject, "body": body}})
    elif mode == "smtp":
        _send_smtp(to, subject, body)
    else:
        raise EmailError(f"Unknown EMAIL_MODE: {mode}")


def _send_smtp(to: str, subject: str, body: str) -> None:
    url = urlparse(settings.smtp_url)
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = settings.email_from, to, subject
    message.set_content(body)
    try:
        with smtplib.SMTP(url.hostname, url.port or 587, timeout=10) as smtp:
            smtp.starttls()
            if url.username:
                smtp.login(unquote(url.username), unquote(url.password or ""))
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailError(str(exc)[:200]) from exc
