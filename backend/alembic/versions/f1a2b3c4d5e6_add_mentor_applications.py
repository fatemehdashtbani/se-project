"""add mentor applications

Revision ID: f1a2b3c4d5e6
Revises: e7b3f9a2c4d6
Create Date: 2026-11-26 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: str | Sequence[str] | None = "e7b3f9a2c4d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the mentor application table."""
    op.create_table(
        "mentor_applications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("expertise", sa.String(length=200), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False),
        sa.Column("documents", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_mentor_applications_user"),
    )
    op.create_index(
        "ix_mentor_applications_user_id",
        "mentor_applications",
        ["user_id"],
        unique=True,
    )
    op.create_index(
        "ix_mentor_applications_status",
        "mentor_applications",
        ["status", "created_at"],
    )


def downgrade() -> None:
    """Drop the mentor application table."""
    op.drop_index(
        "ix_mentor_applications_status", table_name="mentor_applications"
    )
    op.drop_index(
        "ix_mentor_applications_user_id", table_name="mentor_applications"
    )
    op.drop_table("mentor_applications")
