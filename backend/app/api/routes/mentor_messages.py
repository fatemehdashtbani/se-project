"""Mentor message routes (F-035). HTTP concerns only."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.mentor import (
    MentorMessageCreate,
    MentorMessageListResponse,
    MentorMessageResponse,
)
from app.services.mentors import list_messages, send_message

router = APIRouter(prefix="/api/v1/mentor-messages", tags=["mentors"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=MentorMessageListResponse)
async def read_thread(
    current_user: CurrentUserDep,
    session: SessionDep,
    mentor_id: Annotated[uuid.UUID | None, Query()] = None,
    client_id: Annotated[uuid.UUID | None, Query()] = None,
) -> MentorMessageListResponse:
    """Read the pair's thread: users name a mentor, mentors name a client."""
    messages = await list_messages(
        session, current_user, mentor_id=mentor_id, client_id=client_id
    )
    return MentorMessageListResponse(
        items=[MentorMessageResponse.model_validate(message) for message in messages],
        total=len(messages),
    )


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=MentorMessageResponse
)
async def write_message(
    payload: MentorMessageCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MentorMessageResponse:
    """Append a message to a pair's thread; the sender is the caller."""
    message = await send_message(
        session,
        current_user,
        body=payload.body,
        mentor_id=payload.mentor_id,
        client_id=payload.client_id,
    )
    return MentorMessageResponse.model_validate(message)
