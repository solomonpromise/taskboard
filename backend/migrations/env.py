"""Alembic environment: migrations run against DATABASE_URL (book Chapter 10)."""
import sys
from pathlib import Path

from alembic import context

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import models  # noqa: E402,F401  (registers tables)
from app.config import settings  # noqa: E402
from app.db import Base, make_engine  # noqa: E402

config = context.config
url = config.attributes.get("database_url") or settings.database_url


def run_migrations() -> None:
    engine = make_engine(url)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
