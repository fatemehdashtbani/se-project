"""Integration tests for the registration endpoint.

These tests describe the contract from F-019 FR-F019-001 and SPEC section 3.
"""

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.models import User

REGISTER_URL = "/api/v1/auth/register"


async def test_register_creates_user_with_hashed_password(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    response = await client.post(
        REGISTER_URL,
        json={"email": "New.User@Example.com", "password": "secret123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new.user@example.com"
    assert body["role"] == "user"
    assert body["timezone"] == "UTC"
    assert "password" not in body
    assert "password_hash" not in body

    async with db_session_factory() as session:
        user = (
            await session.execute(
                select(User).where(User.email == "new.user@example.com")
            )
        ).scalar_one()

    assert user.password_hash != "secret123"
    assert user.password_hash.startswith("$argon2id$")


async def test_register_rejects_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "duplicate@example.com", "password": "secret123"}

    first = await client.post(REGISTER_URL, json=payload)
    assert first.status_code == 201

    second = await client.post(REGISTER_URL, json=payload)

    assert second.status_code == 400
    assert second.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


async def test_register_rejects_short_password(client: AsyncClient) -> None:
    response = await client.post(
        REGISTER_URL,
        json={"email": "short@example.com", "password": "short"},
    )

    assert response.status_code == 422


async def test_register_rejects_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        REGISTER_URL,
        json={"email": "notanemail", "password": "secret123"},
    )

    assert response.status_code == 422
