"""add routines table

Revision ID: 63b834081a4a
Revises: 9f840ec8f6da
Create Date: 2026-11-22 07:56:56.245927

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "63b834081a4a"
down_revision: str | Sequence[str] | None = "9f840ec8f6da"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the routines table and its owner index."""
    op.create_table(
        "routines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        # ``sa.true()`` and ``CURRENT_TIMESTAMP`` render correctly on both
        # SQLite and PostgreSQL, unlike the literals autogenerate produced.
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_routines_user_id"), "routines", ["user_id"], unique=False)


def downgrade() -> None:
    """Drop the routines table and its index."""
    op.drop_index(op.f("ix_routines_user_id"), table_name="routines")
    op.drop_table("routines")
