"""Routine routes. HTTP concerns only; ownership rules live in the service."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.routine import (
    RoutineCreate,
    RoutineListResponse,
    RoutineResponse,
    RoutineUpdate,
)
from app.services.routines import (
    create_routine,
    delete_routine,
    get_routine,
    list_routines,
    update_routine,
)

router = APIRouter(prefix="/api/v1/routines", tags=["routines"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=RoutineResponse)
async def create(
    payload: RoutineCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> RoutineResponse:
    """Create a routine owned by the signed-in user (FR-F005-001)."""
    routine = await create_routine(
        session,
        current_user,
        title=payload.title,
        description=payload.description,
    )
    return RoutineResponse.model_validate(routine)


@router.get("", response_model=RoutineListResponse)
async def list_own(
    current_user: CurrentUserDep,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RoutineListResponse:
    """List the signed-in user's live routines (FR-F005-002)."""
    routines, total = await list_routines(
        session, current_user, limit=limit, offset=offset
    )
    return RoutineListResponse(
        items=[RoutineResponse.model_validate(routine) for routine in routines],
        total=total,
    )


@router.get("/{routine_id}", response_model=RoutineResponse)
async def get_one(
    routine_id: uuid.UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> RoutineResponse:
    """Return one routine the caller owns."""
    routine = await get_routine(session, current_user, routine_id)
    return RoutineResponse.model_validate(routine)


@router.put("/{routine_id}", response_model=RoutineResponse)
async def update_one(
    routine_id: uuid.UUID,
    payload: RoutineUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> RoutineResponse:
    """Partially update a routine the caller owns (FR-F005-003)."""
    routine = await update_routine(session, current_user, routine_id, payload)
    return RoutineResponse.model_validate(routine)


@router.delete("/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(
    routine_id: uuid.UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> None:
    """Soft-delete a routine the caller owns (FR-F005-004)."""
    await delete_routine(session, current_user, routine_id)
