"""Integration tests for ``PUT /api/v1/auth/me`` (F-031).

The profile form on ``/profile`` used to be display-only; these tests describe
the contract that makes it persist server-side.
"""

from helpers import registration_payload
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.models import User

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"

PASSWORD = "secret123"


async def _signed_in_client(client: AsyncClient, email: str) -> None:
    """Register ``email`` and leave the client holding its session cookies."""
    assert (
        await client.post(REGISTER_URL, json=registration_payload(email))
    ).status_code == 201
    assert (
        await client.post(
            LOGIN_URL, json={"identifier": email, "password": PASSWORD}
        )
    ).status_code == 200


async def test_update_profile_persists_and_is_returned_by_me(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "profile.update@example.com"
    await _signed_in_client(client, email)

    response = await client.put(
        ME_URL,
        json={
            "first_name": "نگار",
            "last_name": "کریمی",
            "phone_number": "0912 345 6789",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "نگار"
    assert body["last_name"] == "کریمی"
    # The same normalization registration applies: spaces and dashes are dropped.
    assert body["phone_number"] == "09123456789"
    assert body["email"] == email

    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
    assert user.first_name == "نگار"
    assert user.last_name == "کریمی"
    assert user.phone_number == "09123456789"

    me = await client.get(ME_URL)
    assert me.status_code == 200
    assert me.json()["first_name"] == "نگار"
    assert me.json()["phone_number"] == "09123456789"


async def test_update_profile_applies_only_the_sent_fields(
    client: AsyncClient,
) -> None:
    email = "profile.partial@example.com"
    await _signed_in_client(client, email)

    response = await client.put(ME_URL, json={"first_name": "سارا"})

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "سارا"
    assert body["last_name"] == "User"
    assert body["phone_number"] == "09120000000"


async def test_update_profile_rejects_blank_or_empty_payloads(
    client: AsyncClient,
) -> None:
    await _signed_in_client(client, "profile.invalid@example.com")

    for payload in ({}, {"first_name": "   "}, {"phone_number": "abc"}, {"first_name": None}):
        response = await client.put(ME_URL, json=payload)

        assert response.status_code == 422, payload
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_update_profile_requires_authentication(client: AsyncClient) -> None:
    response = await client.put(ME_URL, json={"first_name": "نگار"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
