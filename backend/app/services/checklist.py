"""Checklist application services: owner-scoped CRUD (F-033)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.infrastructure.db.models import ChecklistItem, User
from app.schemas.checklist import ChecklistItemUpdate


class ChecklistItemNotFoundError(AppError):
    """Raised for unknown and foreign checklist items alike."""

    status_code = 404
    code = "CHECKLIST_ITEM_NOT_FOUND"
    message = "Checklist item not found."


async def _get_owned_item(
    session: AsyncSession, user: User, item_id: uuid.UUID
) -> ChecklistItem:
    item = await session.scalar(
        select(ChecklistItem).where(
            ChecklistItem.id == item_id, ChecklistItem.user_id == user.id
        )
    )
    if item is None:
        raise ChecklistItemNotFoundError

    return item


async def list_items(session: AsyncSession, user: User) -> list[ChecklistItem]:
    """Return the user's checklist in creation order."""
    rows = await session.scalars(
        select(ChecklistItem)
        .where(ChecklistItem.user_id == user.id)
        .order_by(ChecklistItem.created_at, ChecklistItem.id)
    )
    return list(rows)


async def create_item(session: AsyncSession, user: User, *, title: str) -> ChecklistItem:
    item = ChecklistItem(user_id=user.id, title=title)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def update_item(
    session: AsyncSession,
    user: User,
    item_id: uuid.UUID,
    payload: ChecklistItemUpdate,
) -> ChecklistItem:
    """Apply only the fields the caller actually sent."""
    item = await _get_owned_item(session, user, item_id)

    fields = payload.model_fields_set
    if "title" in fields and payload.title is not None:
        item.title = payload.title
    if "is_done" in fields and payload.is_done is not None:
        item.is_done = payload.is_done

    await session.commit()
    await session.refresh(item)
    return item


async def delete_item(session: AsyncSession, user: User, item_id: uuid.UUID) -> None:
    item = await _get_owned_item(session, user, item_id)

    await session.delete(item)
    await session.commit()
