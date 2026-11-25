"""Mentor directory and consent routes (F-035). HTTP concerns only."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.mentor import (
    MentorClientListResponse,
    MentorClientSummary,
    MentorListResponse,
    MentorSelectionRequest,
    MentorSummary,
    SelectedMentorResponse,
)
from app.services.mentors import (
    display_name,
    get_profile,
    get_selected_mentor,
    list_clients,
    list_mentors,
    revoke_selected_mentor,
    select_mentor,
)

router = APIRouter(prefix="/api/v1/mentors", tags=["mentors"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
MentorDep = Annotated[User, Depends(require_role("mentor"))]


def _summary(user: User, headline: str | None, bio: str | None) -> MentorSummary:
    return MentorSummary(
        id=user.id, name=display_name(user), headline=headline, bio=bio
    )


async def _summary_for(session: AsyncSession, mentor: User) -> MentorSummary:
    profile = await get_profile(session, mentor.id)
    return _summary(
        mentor,
        profile.headline if profile is not None else None,
        profile.bio if profile is not None else None,
    )


@router.get("", response_model=MentorListResponse)
async def list_directory(
    current_user: CurrentUserDep, session: SessionDep
) -> MentorListResponse:
    """List every mentor account and its public profile."""
    rows = await list_mentors(session)
    items = [
        _summary(
            user,
            profile.headline if profile is not None else None,
            profile.bio if profile is not None else None,
        )
        for user, profile in rows
    ]
    return MentorListResponse(items=items, total=len(items))


@router.get("/selected", response_model=SelectedMentorResponse)
async def read_selection(
    current_user: CurrentUserDep, session: SessionDep
) -> SelectedMentorResponse:
    """Return the mentor the caller currently grants access to."""
    mentor = await get_selected_mentor(session, current_user)
    if mentor is None:
        return SelectedMentorResponse(mentor=None)
    return SelectedMentorResponse(mentor=await _summary_for(session, mentor))


@router.put("/selected", response_model=MentorSummary)
async def choose_mentor(
    payload: MentorSelectionRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MentorSummary:
    """Grant consent to one mentor, replacing any previous selection."""
    mentor = await select_mentor(session, current_user, payload.mentor_id)
    return await _summary_for(session, mentor)


@router.delete("/selected", status_code=status.HTTP_204_NO_CONTENT)
async def clear_selection(
    current_user: CurrentUserDep, session: SessionDep
) -> None:
    """Revoke the caller's active mentor grant."""
    await revoke_selected_mentor(session, current_user)


@router.get("/me/clients", response_model=MentorClientListResponse)
async def list_own_clients(
    mentor: MentorDep, session: SessionDep
) -> MentorClientListResponse:
    """List the consenting clients of the calling mentor."""
    clients = await list_clients(session, mentor)
    items = [
        MentorClientSummary(id=client.id, name=display_name(client))
        for client in clients
    ]
    return MentorClientListResponse(items=items, total=len(items))
