"""Mentor collaboration services: directory, consent, chat and programs (F-035).

Every pair-scoped operation resolves the (client, mentor) pair from the
authenticated account and then requires an active, non-revoked grant. The
mentor's very next request after revocation is therefore denied (ADR-0007).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.infrastructure.db.models import (
    MentorGrant,
    MentorMessage,
    MentorProfile,
    MentorProgram,
    Routine,
    User,
)


class MentorNotFoundError(AppError):
    """Raised for unknown accounts and accounts without the mentor role."""

    status_code = 404
    code = "MENTOR_NOT_FOUND"
    message = "Mentor not found."


class MentorAccessDeniedError(AppError):
    """Raised when no active consent grant covers the requested pair."""

    status_code = 403
    code = "MENTOR_ACCESS_DENIED"
    message = "Mentor access requires an active consent grant."


class MentorProgramNotFoundError(AppError):
    """Raised for unknown and foreign programs alike."""

    status_code = 404
    code = "MENTOR_PROGRAM_NOT_FOUND"
    message = "Mentor program not found."


class ProgramAlreadyAdoptedError(AppError):
    """Raised when a program was already turned into a routine."""

    status_code = 409
    code = "PROGRAM_ALREADY_ADOPTED"
    message = "This program has already been adopted."


def display_name(user: User) -> str:
    """Return the name shown to the other side of a conversation."""
    parts = [part for part in (user.first_name, user.last_name) if part]
    if parts:
        return " ".join(parts)
    if user.username:
        return user.username
    return user.email.split("@", 1)[0]


async def list_mentors(
    session: AsyncSession,
) -> list[tuple[User, MentorProfile | None]]:
    """Return every mentor account with its optional public profile."""
    rows = await session.execute(
        select(User, MentorProfile)
        .outerjoin(MentorProfile, MentorProfile.user_id == User.id)
        .where(User.role == "mentor")
        .order_by(User.created_at, User.id)
    )
    return [(user, profile) for user, profile in rows.all()]


async def get_profile(
    session: AsyncSession, mentor_id: uuid.UUID
) -> MentorProfile | None:
    """Return one mentor's public profile row, if it exists."""
    return await session.scalar(
        select(MentorProfile).where(MentorProfile.user_id == mentor_id)
    )


async def _get_mentor(session: AsyncSession, mentor_id: uuid.UUID) -> User:
    mentor = await session.get(User, mentor_id)
    if mentor is None or mentor.role != "mentor":
        raise MentorNotFoundError
    return mentor


async def _active_grant(
    session: AsyncSession, user_id: uuid.UUID, mentor_id: uuid.UUID
) -> MentorGrant | None:
    return await session.scalar(
        select(MentorGrant).where(
            MentorGrant.user_id == user_id,
            MentorGrant.mentor_id == mentor_id,
            MentorGrant.revoked_at.is_(None),
        )
    )


async def get_selected_mentor(session: AsyncSession, user: User) -> User | None:
    """Return the mentor the user currently grants access to, if any."""
    return await session.scalar(
        select(User)
        .join(MentorGrant, MentorGrant.mentor_id == User.id)
        .where(
            MentorGrant.user_id == user.id,
            MentorGrant.revoked_at.is_(None),
        )
        .order_by(MentorGrant.granted_at.desc(), MentorGrant.id)
        .limit(1)
    )


async def select_mentor(
    session: AsyncSession, user: User, mentor_id: uuid.UUID
) -> User:
    """Grant consent to ``mentor_id`` and revoke every other active grant.

    One mentor at a time keeps the consent scope explicit. Re-selecting the
    same mentor is an idempotent update, not a second grant row.
    """
    mentor = await _get_mentor(session, mentor_id)
    now = datetime.now(UTC)

    await session.execute(
        update(MentorGrant)
        .where(
            MentorGrant.user_id == user.id,
            MentorGrant.mentor_id != mentor_id,
            MentorGrant.revoked_at.is_(None),
        )
        .values(revoked_at=now)
        .execution_options(synchronize_session=False)
    )

    grant = await session.scalar(
        select(MentorGrant).where(
            MentorGrant.user_id == user.id,
            MentorGrant.mentor_id == mentor_id,
        )
    )
    if grant is None:
        session.add(MentorGrant(user_id=user.id, mentor_id=mentor_id))
    elif grant.revoked_at is not None:
        grant.revoked_at = None
        grant.granted_at = now

    await session.commit()
    return mentor


async def revoke_selected_mentor(session: AsyncSession, user: User) -> None:
    """Revoke every active grant the user holds. Idempotent."""
    await session.execute(
        update(MentorGrant)
        .where(
            MentorGrant.user_id == user.id,
            MentorGrant.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
        .execution_options(synchronize_session=False)
    )
    await session.commit()


async def list_clients(session: AsyncSession, mentor: User) -> list[User]:
    """Return only the users that granted this mentor access."""
    rows = await session.scalars(
        select(User)
        .join(MentorGrant, MentorGrant.user_id == User.id)
        .where(
            MentorGrant.mentor_id == mentor.id,
            MentorGrant.revoked_at.is_(None),
        )
        .order_by(User.created_at, User.id)
    )
    return list(rows)


async def _resolve_pair(
    session: AsyncSession,
    actor: User,
    *,
    mentor_id: uuid.UUID | None,
    client_id: uuid.UUID | None,
) -> tuple[User, User]:
    """Resolve the (client, mentor) pair for a pair-scoped operation.

    A mentor may only act as themselves and must name a client; a user is always
    the client and must name a mentor. In both cases an active grant is required.
    """
    if actor.role == "mentor":
        if client_id is None:
            raise AppError(
                "client_id is required for a mentor request.",
                code="VALIDATION_ERROR",
                status_code=422,
            )
        if mentor_id is not None and mentor_id != actor.id:
            raise MentorAccessDeniedError

        client = await session.get(User, client_id)
        if client is None or client.id == actor.id:
            raise MentorAccessDeniedError
        mentor = actor
    else:
        if mentor_id is None:
            raise AppError(
                "mentor_id is required.",
                code="VALIDATION_ERROR",
                status_code=422,
            )
        if client_id is not None and client_id != actor.id:
            raise MentorAccessDeniedError

        mentor = await _get_mentor(session, mentor_id)
        client = actor

    if await _active_grant(session, client.id, mentor.id) is None:
        raise MentorAccessDeniedError

    return client, mentor


async def list_messages(
    session: AsyncSession,
    actor: User,
    *,
    mentor_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
) -> list[MentorMessage]:
    """Return one pair's thread in chronological order."""
    client, mentor = await _resolve_pair(
        session, actor, mentor_id=mentor_id, client_id=client_id
    )

    rows = await session.scalars(
        select(MentorMessage)
        .where(
            MentorMessage.user_id == client.id,
            MentorMessage.mentor_id == mentor.id,
        )
        .order_by(MentorMessage.created_at, MentorMessage.id)
    )
    return list(rows)


async def send_message(
    session: AsyncSession,
    actor: User,
    *,
    body: str,
    mentor_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
) -> MentorMessage:
    """Store a message from the authenticated account into one pair's thread."""
    client, mentor = await _resolve_pair(
        session, actor, mentor_id=mentor_id, client_id=client_id
    )

    message = MentorMessage(
        user_id=client.id,
        mentor_id=mentor.id,
        sender_id=actor.id,
        body=body,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def list_programs(
    session: AsyncSession,
    actor: User,
    *,
    client_id: uuid.UUID | None = None,
) -> list[MentorProgram]:
    """Return the programs the caller may see, newest first.

    A user sees the programs sent to them; a mentor sees the programs they sent,
    optionally narrowed to one client.
    """
    query = select(MentorProgram)
    if actor.role == "mentor":
        query = query.where(MentorProgram.mentor_id == actor.id)
        if client_id is not None:
            query = query.where(MentorProgram.user_id == client_id)
    else:
        query = query.where(MentorProgram.user_id == actor.id)

    rows = await session.scalars(
        query.order_by(MentorProgram.created_at.desc(), MentorProgram.id)
    )
    return list(rows)


async def create_program(
    session: AsyncSession,
    mentor: User,
    *,
    client_id: uuid.UUID,
    title: str,
    description: str | None,
    category: str,
) -> MentorProgram:
    """Send a program from a mentor to a client with active consent."""
    client = await session.get(User, client_id)
    if (
        client is None
        or client.id == mentor.id
        or await _active_grant(session, client.id, mentor.id) is None
    ):
        raise MentorAccessDeniedError

    program = MentorProgram(
        user_id=client.id,
        mentor_id=mentor.id,
        title=title,
        description=description,
        category=category,
    )
    session.add(program)
    await session.commit()
    await session.refresh(program)
    return program


async def adopt_program(
    session: AsyncSession, user: User, program_id: uuid.UUID
) -> MentorProgram:
    """Turn one of the user's programs into a routine, once."""
    program = await session.scalar(
        select(MentorProgram).where(
            MentorProgram.id == program_id,
            MentorProgram.user_id == user.id,
        )
    )
    if program is None:
        raise MentorProgramNotFoundError
    if program.routine_id is not None:
        raise ProgramAlreadyAdoptedError

    routine = Routine(
        user_id=user.id,
        title=program.title,
        description=program.description,
    )
    session.add(routine)
    await session.flush()

    program.routine_id = routine.id
    await session.commit()
    await session.refresh(program)
    return program
