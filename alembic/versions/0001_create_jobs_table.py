"""create jobs table

Revision ID: 0001
Revises:
Create Date: 2026-09-15
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("jobs")
