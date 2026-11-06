"""Migrations must build the same schema the code expects, from an empty database."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

BACKEND = Path(__file__).resolve().parent.parent / "backend"


def test_migrations_upgrade_and_downgrade(tmp_path):
    url = f"sqlite:///{tmp_path / 'migrate.db'}"
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "migrations"))
    config.attributes["database_url"] = url

    command.upgrade(config, "head")
    tables = set(inspect(create_engine(url)).get_table_names())
    assert {"users", "tasks", "sessions", "idempotency_keys", "labels", "task_labels", "outbox"} <= tables

    command.downgrade(config, "base")
    assert set(inspect(create_engine(url)).get_table_names()) <= {"alembic_version"}
