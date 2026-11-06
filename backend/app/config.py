"""All configuration comes from environment variables (book Chapter 17)."""
import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv() -> None:
    """Load backend/.env for local development, without overriding real environment variables."""
    path = Path(__file__).resolve().parent.parent / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    database_url: str
    app_env: str
    app_url: str
    cookie_secure: bool
    email_mode: str
    smtp_url: str
    email_from: str

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


def load_settings() -> Settings:
    _load_dotenv()
    settings = Settings(
        database_url=os.environ.get("DATABASE_URL", "sqlite:///./taskboard.db"),
        app_env=os.environ.get("APP_ENV", "development"),
        app_url=os.environ.get("APP_URL", "http://localhost:5173"),
        cookie_secure=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
        email_mode=os.environ.get("EMAIL_MODE", "console"),
        smtp_url=os.environ.get("SMTP_URL", ""),
        email_from=os.environ.get("EMAIL_FROM", "Taskboard <reminders@example.com>"),
    )
    if settings.is_production:
        # Fail loudly rather than run production with development defaults.
        problems = []
        if settings.database_url.startswith("sqlite"):
            problems.append("DATABASE_URL must point to a real database in production")
        if not settings.cookie_secure:
            problems.append("COOKIE_SECURE must be true in production")
        if settings.email_mode == "smtp" and not settings.smtp_url:
            problems.append("SMTP_URL is required when EMAIL_MODE=smtp")
        if problems:
            raise RuntimeError("Unsafe production configuration: " + "; ".join(problems))
    return settings


settings = load_settings()
