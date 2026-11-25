"""add optional event_time to calendar events

Revision ID: d5a2f8c1e6b4
Revises: b7e2c9d4a1f0
Create Date: 2026-11-25 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d5a2f8c1e6b4"
down_revision: str | Sequence[str] | None = "b7e2c9d4a1f0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add the nullable time so existing events keep working unchanged."""
    op.add_column("calendar_events", sa.Column("event_time", sa.Time(), nullable=True))


def downgrade() -> None:
    """Drop the event time."""
    op.drop_column("calendar_events", "event_time")
