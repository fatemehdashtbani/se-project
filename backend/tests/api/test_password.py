"""Integration tests for ``PUT /api/v1/auth/me/password`` (F-031).

Changing the password used to be a UI-only mock. The endpoint must verify the
current password, store a fresh Argon2id hash, and end every other session.
"""

import hashlib

from helpers import registration_payload
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.models import RefreshToken, User

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
ME_URL = "/api/v1/auth/me"
PASSWORD_URL = "/api/v1/auth/me/password"

PASSWORD = "secret123"
NEW_PASSWORD = "both-good-9876"


async def _register(client: AsyncClient, email: str) -> None:
    assert (
        await client.post(REGISTER_URL, json=registration_payload(email))
    ).status_code == 201


async def _login(client: AsyncClient, email: str, password: str = PASSWORD) -> None:
    response = await client.post(
        LOGIN_URL, json={"identifier": email, "password": password}
    )
    assert response.status_code == 200


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def test_change_password_replaces_the_hash_and_the_old_one_stops_working(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "password.change@example.com"
    await _register(client, email)
    await _login(client, email)

    response = await client.put(
        PASSWORD_URL,
        json={"current_password": PASSWORD, "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 200

    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
    assert user.password_hash.startswith("$argon2id$")

    client.cookies.clear()
    old_login = await client.post(
        LOGIN_URL, json={"identifier": email, "password": PASSWORD}
    )
    assert old_login.status_code == 401
    assert old_login.json()["error"]["code"] == "INVALID_CREDENTIALS"

    await _login(client, email, NEW_PASSWORD)
    assert (await client.get(ME_URL)).status_code == 200


async def test_change_password_rejects_a_wrong_current_password(
    client: AsyncClient,
) -> None:
    email = "password.wrong-current@example.com"
    await _register(client, email)
    await _login(client, email)

    response = await client.put(
        PASSWORD_URL,
        json={"current_password": "not-my-password", "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_CURRENT_PASSWORD"

    # The stored password must be untouched.
    client.cookies.clear()
    await _login(client, email, PASSWORD)


async def test_change_password_validates_the_new_password(
    client: AsyncClient,
) -> None:
    await _register(client, "password.validation@example.com")
    await _login(client, "password.validation@example.com")

    for payload in (
        {"current_password": PASSWORD},
        {"current_password": PASSWORD, "new_password": "short"},
        {"new_password": NEW_PASSWORD},
    ):
        response = await client.put(PASSWORD_URL, json=payload)

        assert response.status_code == 422, payload
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_change_password_ends_the_other_sessions_but_keeps_the_current_one(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "password.sessions@example.com"
    await _register(client, email)

    first_login = await client.post(
        LOGIN_URL, json={"identifier": email, "password": PASSWORD}
    )
    assert first_login.status_code == 200
    older_token = first_login.cookies["refresh_token"]

    # A second sign-in starts a separate token family; its cookies are the ones
    # the client now carries.
    await _login(client, email)

    response = await client.put(
        PASSWORD_URL,
        json={"current_password": PASSWORD, "new_password": NEW_PASSWORD},
    )
    assert response.status_code == 200

    current_token = client.cookies["refresh_token"]

    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
        rows = (
            (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.user_id == user.id)
                )
            )
            .scalars()
            .all()
        )

    by_hash = {row.token_hash: row for row in rows}
    assert by_hash[_hash(older_token)].revoked_at is not None
    assert by_hash[_hash(current_token)].revoked_at is None

    refreshed = await client.post(REFRESH_URL)
    assert refreshed.status_code == 200


async def test_change_password_requires_authentication(client: AsyncClient) -> None:
    response = await client.put(
        PASSWORD_URL,
        json={"current_password": PASSWORD, "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
