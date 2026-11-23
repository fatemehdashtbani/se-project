"""Routine application services: owner-scoped CRUD (F-005)."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.infrastructure.db.models import Routine, User
from app.schemas.routine import RoutineUpdate


class RoutineNotFoundError(AppError):
    """Raised for unknown, soft-deleted, and foreign routines alike.

    The three cases are deliberately indistinguishable: answering 403 for
    somebody else's id would confirm that the routine exists (FR-F005-005).
    """

    status_code = 404
    code = "ROUTINE_NOT_FOUND"
    message = "Routine not found."


async def _get_owned_routine(
    session: AsyncSession, user: User, routine_id: uuid.UUID
) -> Routine:
    """Return the routine only when it is live and belongs to ``user``."""
    routine = await session.scalar(
        select(Routine).where(
            Routine.id == routine_id,
            Routine.user_id == user.id,
            Routine.deleted_at.is_(None),
        )
    )
    if routine is None:
        raise RoutineNotFoundError

    return routine


async def create_routine(
    session: AsyncSession,
    user: User,
    *,
    title: str,
    description: str | None,
) -> Routine:
    """Store a new routine for ``user`` (FR-F005-001)."""
    routine = Routine(user_id=user.id, title=title, description=description)
    session.add(routine)
    await session.commit()
    await session.refresh(routine)
    return routine


async def list_routines(
    session: AsyncSession, user: User, *, limit: int, offset: int
) -> tuple[list[Routine], int]:
    """Return one page of the user's live routines and their total count."""
    conditions = (Routine.user_id == user.id, Routine.deleted_at.is_(None))

    total = await session.scalar(
        select(func.count()).select_from(Routine).where(*conditions)
    )
    rows = await session.scalars(
        select(Routine)
        .where(*conditions)
        .order_by(Routine.created_at, Routine.id)
        .limit(limit)
        .offset(offset)
    )

    return list(rows), int(total or 0)


async def get_routine(
    session: AsyncSession, user: User, routine_id: uuid.UUID
) -> Routine:
    """Return one owned routine (FR-F005-002)."""
    return await _get_owned_routine(session, user, routine_id)


async def update_routine(
    session: AsyncSession,
    user: User,
    routine_id: uuid.UUID,
    payload: RoutineUpdate,
) -> Routine:
    """Apply only the fields the caller actually sent (FR-F005-003)."""
    routine = await _get_owned_routine(session, user, routine_id)

    fields = payload.model_fields_set
    if "title" in fields and payload.title is not None:
        routine.title = payload.title
    if "description" in fields:
        routine.description = payload.description

    await session.commit()
    await session.refresh(routine)
    return routine


async def delete_routine(
    session: AsyncSession, user: User, routine_id: uuid.UUID
) -> None:
    """Soft-delete an owned routine (FR-F005-004).

    The row is kept so future check-ins still reference a real routine; only its
    visibility changes.
    """
    routine = await _get_owned_routine(session, user, routine_id)

    routine.deleted_at = datetime.now(UTC)
    routine.is_active = False
    await session.commit()
