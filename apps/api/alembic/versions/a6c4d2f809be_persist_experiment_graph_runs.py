"""persist experiment graph run details

Revision ID: a6c4d2f809be
Revises: 95f90d6fa00b
Create Date: 2026-09-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a6c4d2f809be"
down_revision: str | None = "95f90d6fa00b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "experiments",
        "status",
        existing_type=sa.String(length=20),
        type_=sa.String(length=40),
        existing_nullable=False,
    )
    op.add_column("experiments", sa.Column("completed_at", sa.DateTime(timezone=True)))
    op.add_column(
        "experiments",
        sa.Column(
            "execution_trace",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "experiments",
        sa.Column(
            "node_outputs",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "experiments",
        sa.Column(
            "constraints",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column("experiments", sa.Column("run_fingerprint", sa.String(length=64)))
    op.add_column("experiments", sa.Column("last_completed_node", sa.String(length=100)))
    op.add_column(
        "experiments",
        sa.Column(
            "errors",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.execute(
        "UPDATE experiments SET status = 'completed' "
        "WHERE status = 'completed_with_constraints'"
    )
    op.drop_column("experiments", "errors")
    op.drop_column("experiments", "last_completed_node")
    op.drop_column("experiments", "run_fingerprint")
    op.drop_column("experiments", "constraints")
    op.drop_column("experiments", "node_outputs")
    op.drop_column("experiments", "execution_trace")
    op.drop_column("experiments", "completed_at")
    op.alter_column(
        "experiments",
        "status",
        existing_type=sa.String(length=40),
        type_=sa.String(length=20),
        existing_nullable=False,
    )
