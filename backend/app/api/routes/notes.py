"""Note routes. HTTP concerns only; ownership rules live in the service."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.note import (
    NoteCreate,
    NoteListResponse,
    NoteResponse,
    NoteUpdate,
)
from app.services.notes import create_note, delete_note, list_notes, update_note

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=NoteListResponse)
async def list_own(current_user: CurrentUserDep, session: SessionDep) -> NoteListResponse:
    """List the signed-in user's notes."""
    notes = await list_notes(session, current_user)
    return NoteListResponse(
        items=[NoteResponse.model_validate(note) for note in notes],
        total=len(notes),
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NoteResponse)
async def create(
    payload: NoteCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> NoteResponse:
    """Create a note owned by the signed-in user."""
    note = await create_note(
        session, current_user, title=payload.title, content=payload.content
    )
    return NoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_one(
    note_id: uuid.UUID,
    payload: NoteUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> NoteResponse:
    """Edit a note the caller owns."""
    note = await update_note(session, current_user, note_id, payload)
    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(
    note_id: uuid.UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> None:
    """Delete a note the caller owns."""
    await delete_note(session, current_user, note_id)
