"""Mentor application routes (F-036). HTTP concerns only."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.infrastructure.db.models import MentorApplication, User
from app.infrastructure.db.session import get_session
from app.schemas.mentor_application import (
    AdminMentorApplicationResponse,
    ApplicationStatus,
    MentorApplicationCreate,
    MentorApplicationListResponse,
    MentorApplicationResponse,
    MyMentorApplicationResponse,
)
from app.services.mentor_applications import (
    approve_application,
    get_application,
    list_applications,
    reject_application,
    submit_application,
)
from app.services.mentors import display_name

router = APIRouter(
    prefix="/api/v1/mentor-applications", tags=["mentor-applications"]
)
admin_router = APIRouter(prefix="/api/v1/admin/mentor-applications", tags=["admin"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
ApplicantDep = Annotated[User, Depends(require_role("user"))]
AdminDep = Annotated[User, Depends(require_role("admin"))]


def _admin_item(
    application: MentorApplication, applicant: User
) -> AdminMentorApplicationResponse:
    """Combine an application with the identity of the account that sent it."""
    return AdminMentorApplicationResponse(
        **MentorApplicationResponse.model_validate(application).model_dump(),
        applicant_name=display_name(applicant),
        applicant_email=applicant.email,
    )


@router.get("/me", response_model=MyMentorApplicationResponse)
async def read_my_application(
    current_user: CurrentUserDep, session: SessionDep
) -> MyMentorApplicationResponse:
    """Return the caller's application and its current status."""
    application = await get_application(session, current_user)
    return MyMentorApplicationResponse(
        application=(
            MentorApplicationResponse.model_validate(application)
            if application is not None
            else None
        )
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=MentorApplicationResponse,
)
async def submit_mentor_application(
    payload: MentorApplicationCreate,
    current_user: ApplicantDep,
    session: SessionDep,
) -> MentorApplicationResponse:
    """Submit (or resubmit) the caller's mentor request as pending."""
    application = await submit_application(
        session,
        current_user,
        expertise=payload.expertise,
        bio=payload.bio,
        documents=payload.documents,
    )
    return MentorApplicationResponse.model_validate(application)


@admin_router.get("", response_model=MentorApplicationListResponse)
async def list_mentor_applications(
    admin: AdminDep,
    session: SessionDep,
    status_filter: Annotated[ApplicationStatus | None, Query(alias="status")] = None,
) -> MentorApplicationListResponse:
    """List applications for review, optionally narrowed to one status."""
    rows = await list_applications(session, status=status_filter)
    items = [_admin_item(application, applicant) for application, applicant in rows]
    return MentorApplicationListResponse(items=items, total=len(items))


@admin_router.post(
    "/{application_id}/approve", response_model=MentorApplicationResponse
)
async def approve_mentor_application(
    application_id: uuid.UUID, admin: AdminDep, session: SessionDep
) -> MentorApplicationResponse:
    """Approve an application and grant the mentor role."""
    application = await approve_application(session, admin, application_id)
    return MentorApplicationResponse.model_validate(application)


@admin_router.post(
    "/{application_id}/reject", response_model=MentorApplicationResponse
)
async def reject_mentor_application(
    application_id: uuid.UUID, admin: AdminDep, session: SessionDep
) -> MentorApplicationResponse:
    """Reject a pending application, leaving the account a regular user."""
    application = await reject_application(session, admin, application_id)
    return MentorApplicationResponse.model_validate(application)
