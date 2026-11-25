"""Checklist routes. HTTP concerns only; ownership rules live in the service."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.checklist import (
    ChecklistItemCreate,
    ChecklistItemResponse,
    ChecklistItemUpdate,
    ChecklistListResponse,
)
from app.services.checklist import (
    create_item,
    delete_item,
    list_items,
    update_item,
)

router = APIRouter(prefix="/api/v1/checklist-items", tags=["checklist"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=ChecklistListResponse)
async def list_own(
    current_user: CurrentUserDep, session: SessionDep
) -> ChecklistListResponse:
    """Return the signed-in user's checklist with its done/total counters."""
    items = await list_items(session, current_user)
    return ChecklistListResponse(
        items=[ChecklistItemResponse.model_validate(item) for item in items],
        total=len(items),
        done=sum(1 for item in items if item.is_done),
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ChecklistItemResponse)
async def create(
    payload: ChecklistItemCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> ChecklistItemResponse:
    """Add one item to the caller's checklist."""
    item = await create_item(session, current_user, title=payload.title)
    return ChecklistItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=ChecklistItemResponse)
async def update_one(
    item_id: uuid.UUID,
    payload: ChecklistItemUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> ChecklistItemResponse:
    """Rename an item or tick it off."""
    item = await update_item(session, current_user, item_id, payload)
    return ChecklistItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(
    item_id: uuid.UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> None:
    """Remove an item the caller owns."""
    await delete_item(session, current_user, item_id)
