"""Mentor program routes (F-035). HTTP concerns only."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_role
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.mentor import (
    MentorProgramCreate,
    MentorProgramListResponse,
    MentorProgramResponse,
)
from app.services.mentors import adopt_program, create_program, list_programs

router = APIRouter(prefix="/api/v1/mentor-programs", tags=["mentors"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
MentorDep = Annotated[User, Depends(require_role("mentor"))]


@router.get("", response_model=MentorProgramListResponse)
async def list_own(
    current_user: CurrentUserDep,
    session: SessionDep,
    client_id: Annotated[uuid.UUID | None, Query()] = None,
) -> MentorProgramListResponse:
    """List programs sent to the caller, or sent by the calling mentor."""
    programs = await list_programs(session, current_user, client_id=client_id)
    return MentorProgramListResponse(
        items=[
            MentorProgramResponse.model_validate(program) for program in programs
        ],
        total=len(programs),
    )


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=MentorProgramResponse
)
async def create(
    payload: MentorProgramCreate,
    mentor: MentorDep,
    session: SessionDep,
) -> MentorProgramResponse:
    """Send a program to a consenting client."""
    program = await create_program(
        session,
        mentor,
        client_id=payload.client_id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
    )
    return MentorProgramResponse.model_validate(program)


@router.post("/{program_id}/adopt", response_model=MentorProgramResponse)
async def adopt(
    program_id: uuid.UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MentorProgramResponse:
    """Turn one of the caller's programs into a routine."""
    program = await adopt_program(session, current_user, program_id)
    return MentorProgramResponse.model_validate(program)
