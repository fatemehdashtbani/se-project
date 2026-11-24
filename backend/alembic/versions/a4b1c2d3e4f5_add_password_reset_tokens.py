"""add password reset tokens

Revision ID: a4b1c2d3e4f5
Revises: c7d18ab07c7d
Create Date: 2026-11-24 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4b1c2d3e4f5"
down_revision: str | Sequence[str] | None = "c7d18ab07c7d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the single-use reset-token table (F-022)."""
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_password_reset_tokens_token_hash",
        "password_reset_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"]
    )


def downgrade() -> None:
    """Drop the reset-token table."""
    op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")
    op.drop_index(
        "ix_password_reset_tokens_token_hash", table_name="password_reset_tokens"
    )
    op.drop_table("password_reset_tokens")
