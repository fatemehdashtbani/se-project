"""Calendar event application services: owner-scoped CRUD (F-033)."""

import uuid
from datetime import date, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.infrastructure.db.models import CalendarEvent, User


class CalendarEventNotFoundError(AppError):
    """Raised for unknown and foreign calendar events alike."""

    status_code = 404
    code = "CALENDAR_EVENT_NOT_FOUND"
    message = "Calendar event not found."


async def _get_owned_event(
    session: AsyncSession, user: User, event_id: uuid.UUID
) -> CalendarEvent:
    event = await session.scalar(
        select(CalendarEvent).where(
            CalendarEvent.id == event_id, CalendarEvent.user_id == user.id
        )
    )
    if event is None:
        raise CalendarEventNotFoundError

    return event


async def list_events(
    session: AsyncSession,
    user: User,
    *,
    start: date | None = None,
    end: date | None = None,
) -> list[CalendarEvent]:
    """Return the user's events, optionally limited to a date window."""
    query = select(CalendarEvent).where(CalendarEvent.user_id == user.id)
    if start is not None:
        query = query.where(CalendarEvent.event_date >= start)
    if end is not None:
        query = query.where(CalendarEvent.event_date <= end)

    rows = await session.scalars(
        query.order_by(CalendarEvent.event_date, CalendarEvent.created_at)
    )
    return list(rows)


async def create_event(
    session: AsyncSession,
    user: User,
    *,
    title: str,
    event_date: date,
    event_time: time | None = None,
) -> CalendarEvent:
    event = CalendarEvent(
        user_id=user.id, title=title, event_date=event_date, event_time=event_time
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event



async def delete_event(
    session: AsyncSession, user: User, event_id: uuid.UUID
) -> None:
    event = await _get_owned_event(session, user, event_id)

    await session.delete(event)
    await session.commit()
