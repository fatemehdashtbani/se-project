"""Note application services: owner-scoped CRUD (F-033)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.infrastructure.db.models import Note, User
from app.schemas.note import NoteUpdate


class NoteNotFoundError(AppError):
    """Raised for unknown and foreign notes alike."""

    status_code = 404
    code = "NOTE_NOT_FOUND"
    message = "Note not found."


async def _get_owned_note(session: AsyncSession, user: User, note_id: uuid.UUID) -> Note:
    note = await session.scalar(
        select(Note).where(Note.id == note_id, Note.user_id == user.id)
    )
    if note is None:
        raise NoteNotFoundError

    return note


async def list_notes(session: AsyncSession, user: User) -> list[Note]:
    """Return the user's notes, most recently edited first."""
    rows = await session.scalars(
        select(Note)
        .where(Note.user_id == user.id)
        .order_by(Note.updated_at.desc(), Note.created_at.desc(), Note.id)
    )
    return list(rows)


async def create_note(
    session: AsyncSession, user: User, *, title: str, content: str
) -> Note:
    note = Note(user_id=user.id, title=title, content=content)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def update_note(
    session: AsyncSession, user: User, note_id: uuid.UUID, payload: NoteUpdate
) -> Note:
    """Apply only the fields the caller actually sent."""
    note = await _get_owned_note(session, user, note_id)

    fields = payload.model_fields_set
    if "title" in fields and payload.title is not None:
        note.title = payload.title
    if "content" in fields and payload.content is not None:
        note.content = payload.content

    await session.commit()
    await session.refresh(note)
    return note


async def delete_note(session: AsyncSession, user: User, note_id: uuid.UUID) -> None:
    note = await _get_owned_note(session, user, note_id)

    await session.delete(note)
    await session.commit()
