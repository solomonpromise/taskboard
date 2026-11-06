"""Labels and the task_labels linking table.

Revision ID: 0003
"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade() -> None:
    op.create_table(
        "labels",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(40), nullable=False),
        sa.UniqueConstraint("owner_id", "name", name="labels_owner_name_key"),
    )
    op.create_index("ix_labels_owner_id", "labels", ["owner_id"])
    op.create_table(
        "task_labels",
        sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("label_id", sa.Integer, sa.ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("task_labels")
    op.drop_index("ix_labels_owner_id", table_name="labels")
    op.drop_table("labels")
