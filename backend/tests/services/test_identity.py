"""Tests for identity services added by F-003 (admin promotion).

The CLI wrapper is verified manually; these tests pin the decision logic.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.models import User
from app.services.identity import UserNotFoundError, promote_to_admin, register_user

PASSWORD = "secret123"
EMAIL = "promotable@example.com"


async def _register(
    db_session_factory: async_sessionmaker[AsyncSession], email: str = EMAIL
) -> None:
    async with db_session_factory() as session:
        await register_user(session, email=email, password=PASSWORD)


async def _role_of(
    db_session_factory: async_sessionmaker[AsyncSession], email: str = EMAIL
) -> str:
    async with db_session_factory() as session:
        user = await session.scalar(select(User).where(User.email == email))
        assert user is not None
        return user.role


async def test_promote_to_admin_promotes_a_regular_user(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(db_session_factory)

    async with db_session_factory() as session:
        changed = await promote_to_admin(session, email=EMAIL)

    assert changed is True
    assert await _role_of(db_session_factory) == "admin"


async def test_promote_to_admin_is_idempotent(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(db_session_factory)

    async with db_session_factory() as session:
        first = await promote_to_admin(session, email=EMAIL)
    async with db_session_factory() as session:
        second = await promote_to_admin(session, email=EMAIL)

    assert (first, second) == (True, False)
    assert await _role_of(db_session_factory) == "admin"


async def test_promote_to_admin_rejects_an_unknown_email(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with db_session_factory() as session:
        with pytest.raises(UserNotFoundError):
            await promote_to_admin(session, email="ghost@example.com")
