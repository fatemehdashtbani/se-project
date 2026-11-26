"""Mentor application services: submit, review, and promote (F-036).

A user asks to become a mentor; an administrator approves or rejects the
request. Only approval changes ``User.role``, and it also upserts the public
``MentorProfile`` so the new mentor is immediately discoverable (F-035).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.infrastructure.db.models import MentorApplication, MentorProfile, User


class MentorApplicationNotFoundError(AppError):
    """Raised for an unknown application id."""

    status_code = 404
    code = "MENTOR_APPLICATION_NOT_FOUND"
    message = "Mentor application not found."


class MentorApplicationNotPendingError(AppError):
    """Raised when a reviewed application is reviewed again."""

    status_code = 409
    code = "MENTOR_APPLICATION_NOT_PENDING"
    message = "This mentor application has already been reviewed."


class AlreadyMentorError(AppError):
    """Raised when a mentor account tries to apply again."""

    status_code = 409
    code = "ALREADY_MENTOR"
    message = "This account already has the mentor role."


async def get_application(
    session: AsyncSession, user: User
) -> MentorApplication | None:
    """Return the caller's application row, whatever its review state."""
    return await session.scalar(
        select(MentorApplication).where(MentorApplication.user_id == user.id)
    )


async def submit_application(
    session: AsyncSession,
    user: User,
    *,
    expertise: str,
    bio: str,
    documents: str | None,
) -> MentorApplication:
    """Create or refresh the caller's application and mark it pending.

    A rejected request can be resubmitted with new details; resubmitting while
    a decision is pending updates the same row instead of queueing a duplicate.
    """
    if user.role == "mentor":
        raise AlreadyMentorError

    application = await get_application(session, user)
    if application is None:
        application = MentorApplication(
            user_id=user.id,
            expertise=expertise,
            bio=bio,
            documents=documents,
            status="pending",
        )
        session.add(application)
    else:
        if application.status == "approved":
            # The role should already be mentor; refuse instead of silently
            # demoting a mentor back into the review queue.
            raise AlreadyMentorError
        application.expertise = expertise
        application.bio = bio
        application.documents = documents
        application.status = "pending"
        application.reviewed_at = None
        application.reviewed_by = None

    await session.commit()
    await session.refresh(application)
    return application


async def list_applications(
    session: AsyncSession, *, status: str | None = None
) -> list[tuple[MentorApplication, User]]:
    """Return applications with their applicant, oldest first."""
    query = select(MentorApplication, User).join(
        User, User.id == MentorApplication.user_id
    )
    if status is not None:
        query = query.where(MentorApplication.status == status)

    rows = await session.execute(
        query.order_by(MentorApplication.created_at, MentorApplication.id)
    )
    return [(application, applicant) for application, applicant in rows.all()]


async def _get_pending(
    session: AsyncSession, application_id: uuid.UUID
) -> MentorApplication:
    """Load one application that still awaits a decision."""
    application = await session.get(MentorApplication, application_id)
    if application is None:
        raise MentorApplicationNotFoundError
    if application.status != "pending":
        raise MentorApplicationNotPendingError
    return application


async def approve_application(
    session: AsyncSession, admin: User, application_id: uuid.UUID
) -> MentorApplication:
    """Approve one application, promote the applicant, and publish the profile."""
    application = await _get_pending(session, application_id)

    applicant = await session.get(User, application.user_id)
    if applicant is None:
        raise MentorApplicationNotFoundError

    applicant.role = "mentor"

    profile = await session.scalar(
        select(MentorProfile).where(MentorProfile.user_id == applicant.id)
    )
    headline = application.expertise[:120]
    if profile is None:
        session.add(
            MentorProfile(
                user_id=applicant.id,
                headline=headline,
                bio=application.bio,
            )
        )
    else:
        profile.headline = headline
        profile.bio = application.bio

    application.status = "approved"
    application.reviewed_at = datetime.now(UTC)
    application.reviewed_by = admin.id

    await session.commit()
    await session.refresh(application)
    return application


async def reject_application(
    session: AsyncSession, admin: User, application_id: uuid.UUID
) -> MentorApplication:
    """Reject one pending application without changing the applicant's role."""
    application = await _get_pending(session, application_id)

    application.status = "rejected"
    application.reviewed_at = datetime.now(UTC)
    application.reviewed_by = admin.id

    await session.commit()
    await session.refresh(application)
    return application
