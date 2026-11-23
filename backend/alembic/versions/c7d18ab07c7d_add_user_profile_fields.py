"""add user profile fields

Revision ID: c7d18ab07c7d
Revises: 63b834081a4a
Create Date: 2026-11-23 07:15:35.305299

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c7d18ab07c7d"
down_revision: str | Sequence[str] | None = "63b834081a4a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the registration-form profile fields.

    All four columns are nullable so accounts created before this feature stay
    valid; ``username`` is unique through its index.
    """
    op.add_column("users", sa.Column("username", sa.String(length=50), nullable=True))
    op.add_column(
        "users", sa.Column("first_name", sa.String(length=100), nullable=True)
    )
    op.add_column("users", sa.Column("last_name", sa.String(length=100), nullable=True))
    op.add_column(
        "users", sa.Column("phone_number", sa.String(length=20), nullable=True)
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    """Drop the profile fields."""
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "phone_number")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    op.drop_column("users", "username")
