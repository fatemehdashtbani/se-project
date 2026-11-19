"""add family_id to refresh_tokens

Revision ID: 9f840ec8f6da
Revises: 58587b93cd29
Create Date: 2026-11-19 09:53:08.950110

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f840ec8f6da"
down_revision: str | Sequence[str] | None = "58587b93cd29"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add a token-family id so replay revocation is scoped to one login chain."""
    op.add_column("refresh_tokens", sa.Column("family_id", sa.String(), nullable=True))

    # Give every pre-existing token its own family before enforcing NOT NULL.
    bind = op.get_bind()
    rows = sa.table(
        "refresh_tokens",
        sa.column("id", sa.Uuid()),
        sa.column("family_id", sa.String()),
    )
    for token_id in bind.execute(sa.select(rows.c.id)).scalars().all():
        bind.execute(
            rows.update()
            .where(rows.c.id == token_id)
            .values(family_id=str(uuid.uuid4()))
        )

    with op.batch_alter_table("refresh_tokens", recreate="auto") as batch_op:
        batch_op.alter_column("family_id", existing_type=sa.String(), nullable=False)
        batch_op.create_index(
            batch_op.f("ix_refresh_tokens_family_id"), ["family_id"], unique=False
        )


def downgrade() -> None:
    """Drop the token-family id."""
    with op.batch_alter_table("refresh_tokens", recreate="auto") as batch_op:
        batch_op.drop_index(batch_op.f("ix_refresh_tokens_family_id"))
        batch_op.drop_column("family_id")
