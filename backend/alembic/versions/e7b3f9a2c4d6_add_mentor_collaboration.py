"""add mentor collaboration tables

Revision ID: e7b3f9a2c4d6
Revises: d5a2f8c1e6b4
Create Date: 2026-11-25 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7b3f9a2c4d6"
down_revision: str | Sequence[str] | None = "d5a2f8c1e6b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the mentor profile, consent, message and program tables."""
    op.create_table(
        "mentor_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("headline", sa.String(length=120), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        "ix_mentor_profiles_user_id", "mentor_profiles", ["user_id"], unique=True
    )

    op.create_table(
        "mentor_grants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("mentor_id", sa.Uuid(), nullable=False),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mentor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "mentor_id", name="uq_mentor_grants_pair"),
    )
    op.create_index("ix_mentor_grants_user_id", "mentor_grants", ["user_id"])
    op.create_index("ix_mentor_grants_mentor_id", "mentor_grants", ["mentor_id"])

    op.create_table(
        "mentor_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("mentor_id", sa.Uuid(), nullable=False),
        sa.Column("sender_id", sa.Uuid(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mentor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_mentor_messages_thread",
        "mentor_messages",
        ["user_id", "mentor_id", "created_at"],
    )

    op.create_table(
        "mentor_programs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("mentor_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column("routine_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mentor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["routine_id"], ["routines.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_mentor_programs_pair", "mentor_programs", ["user_id", "mentor_id"]
    )


def downgrade() -> None:
    """Drop the mentor collaboration tables."""
    op.drop_index("ix_mentor_programs_pair", table_name="mentor_programs")
    op.drop_table("mentor_programs")

    op.drop_index("ix_mentor_messages_thread", table_name="mentor_messages")
    op.drop_table("mentor_messages")

    op.drop_index("ix_mentor_grants_mentor_id", table_name="mentor_grants")
    op.drop_index("ix_mentor_grants_user_id", table_name="mentor_grants")
    op.drop_table("mentor_grants")

    op.drop_index("ix_mentor_profiles_user_id", table_name="mentor_profiles")
    op.drop_table("mentor_profiles")
