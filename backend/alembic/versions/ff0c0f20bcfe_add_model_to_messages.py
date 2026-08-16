"""Add model to messages

Revision ID: ff0c0f20bcfe
Revises: 2388508dfcf3
Create Date: 2026-08-15 07:30:25.950234
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ff0c0f20bcfe"
down_revision: str | Sequence[str] | None = "2388508dfcf3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add model column to messages table."""

    op.add_column(
        "messages",
        sa.Column(
            "model",
            sa.String(length=100),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove model column from messages table."""

    op.drop_column(
        "messages",
        "model",
    )
