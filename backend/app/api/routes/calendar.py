"""Calendar routes. HTTP concerns only; ownership rules live in the service."""

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventListResponse,
    CalendarEventResponse,
)
from app.services.calendar import create_event, delete_event, list_events

router = APIRouter(prefix="/api/v1/calendar-events", tags=["calendar"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=CalendarEventListResponse)
async def list_own(
    current_user: CurrentUserDep,
    session: SessionDep,
    start: Annotated[date | None, Query()] = None,
    end: Annotated[date | None, Query()] = None,
) -> CalendarEventListResponse:
    """List the caller's events, optionally inside ``start``..``end``."""
    events = await list_events(session, current_user, start=start, end=end)
    return CalendarEventListResponse(
        items=[CalendarEventResponse.model_validate(event) for event in events],
        total=len(events),
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CalendarEventResponse)
async def create(
    payload: CalendarEventCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> CalendarEventResponse:
    """Create a dated event owned by the signed-in user."""
    event = await create_event(
        session,
        current_user,
        title=payload.title,
        event_date=payload.event_date,
        event_time=payload.event_time,
    )
    return CalendarEventResponse.model_validate(event)



@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(
    event_id: uuid.UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> None:
    """Delete an event the caller owns."""
    await delete_event(session, current_user, event_id)
