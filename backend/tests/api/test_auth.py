"""Integration tests for the registration and login endpoints.

These tests describe the contract from F-019 FR-F019-001, FR-F019-002 and SPEC section 3.
"""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from httpx import AsyncClient, Response
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.infrastructure.db.models import RefreshToken, User

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
ME_URL = "/api/v1/auth/me"
LOGOUT_URL = "/api/v1/auth/logout"

PASSWORD = "secret123"


async def _register_user(
    client: AsyncClient, email: str, password: str = PASSWORD
) -> Response:
    return await client.post(REGISTER_URL, json={"email": email, "password": password})


async def _login(client: AsyncClient, email: str, password: str = PASSWORD) -> Response:
    return await client.post(LOGIN_URL, json={"email": email, "password": password})


def _set_cookie_headers(response: Response) -> dict[str, str]:
    """Map cookie name to its raw ``Set-Cookie`` header."""
    headers: dict[str, str] = {}
    for raw in response.headers.get_list("set-cookie"):
        name = raw.split("=", 1)[0].strip()
        headers[name] = raw
    return headers


def _cookie_payload(header: str) -> str:
    """Return the (unquoted) value portion of a raw ``Set-Cookie`` header."""
    pair = header.split(";", 1)[0]
    _, _, value = pair.partition("=")
    return value.strip().strip('"')


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def _refresh_rows(
    db_session_factory: async_sessionmaker[AsyncSession],
    email: str,
) -> dict[str, RefreshToken]:
    """Return this user's refresh-token rows keyed by token hash."""
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

    return {row.token_hash: row for row in rows}


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
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_register_rejects_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        REGISTER_URL,
        json={"email": "notanemail", "password": "secret123"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_login_returns_http_only_cookies_and_records_refresh_token(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "login.user@example.com"
    assert (await _register_user(client, email)).status_code == 201

    response = await client.post(LOGIN_URL, json={"email": email, "password": PASSWORD})

    assert response.status_code == 200

    cookie_headers = _set_cookie_headers(response)
    assert "access_token" in cookie_headers
    assert "refresh_token" in cookie_headers
    assert "httponly" in cookie_headers["access_token"].lower()
    assert "httponly" in cookie_headers["refresh_token"].lower()

    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
        tokens = (
            (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.user_id == user.id)
                )
            )
            .scalars()
            .all()
        )

    assert len(tokens) == 1
    refresh_row = tokens[0]
    assert refresh_row.revoked_at is None

    expires_at = refresh_row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    assert expires_at > datetime.now(UTC)

    refresh_cookie = response.cookies["refresh_token"]
    assert refresh_row.token_hash == hashlib.sha256(refresh_cookie.encode()).hexdigest()
    assert len(refresh_row.token_hash) == 64


async def test_login_rejects_wrong_password(client: AsyncClient) -> None:
    email = "wrong.password@example.com"
    assert (await _register_user(client, email)).status_code == 201

    response = await client.post(
        LOGIN_URL,
        json={"email": email, "password": "different-secret"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_login_rejects_unknown_email_without_disclosing_it(
    client: AsyncClient,
) -> None:
    response = await client.post(
        LOGIN_URL,
        json={"email": "nobody@example.com", "password": PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_me_returns_current_user(client: AsyncClient) -> None:
    email = "me.valid@example.com"
    registration = await _register_user(client, email)
    user_id = registration.json()["id"]

    assert (await _login(client, email)).status_code == 200

    response = await client.get(ME_URL)

    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "email": email,
        "role": "user",
        "timezone": "UTC",
    }


async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get(ME_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] in {"UNAUTHORIZED", "NOT_AUTHENTICATED"}


async def test_me_rejects_expired_token(client: AsyncClient) -> None:
    settings = get_settings()
    expired_token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    response = await client.get(
        ME_URL,
        headers={"Cookie": f"access_token={expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "TOKEN_EXPIRED"


async def test_logout_clears_cookies_and_revokes_refresh_token(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "logout@example.com"
    assert (await _register_user(client, email)).status_code == 201
    assert (await _login(client, email)).status_code == 200

    response = await client.post(LOGOUT_URL)

    assert response.status_code in {200, 204}

    cookie_headers = _set_cookie_headers(response)
    for name in ("access_token", "refresh_token"):
        assert name in cookie_headers
        assert _cookie_payload(cookie_headers[name]) == ""
        assert "max-age=0" in cookie_headers[name].lower()

    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
        tokens = (
            (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.user_id == user.id)
                )
            )
            .scalars()
            .all()
        )

    assert len(tokens) == 1
    assert tokens[0].revoked_at is not None


async def test_refresh_rotates_tokens_and_revokes_the_previous_row(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "refresh.valid@example.com"
    assert (await _register_user(client, email)).status_code == 201
    login = await _login(client, email)
    assert login.status_code == 200

    old_refresh = login.cookies["refresh_token"]
    old_hash = _hash_token(old_refresh)

    response = await client.post(REFRESH_URL)

    assert response.status_code == 200

    cookie_headers = _set_cookie_headers(response)
    assert "access_token" in cookie_headers
    assert "refresh_token" in cookie_headers

    new_refresh = _cookie_payload(cookie_headers["refresh_token"])
    new_hash = _hash_token(new_refresh)
    assert new_refresh != old_refresh

    rows = await _refresh_rows(db_session_factory, email)

    assert old_hash in rows
    assert new_hash in rows
    assert len(rows) == 2
    assert rows[old_hash].revoked_at is not None
    assert rows[new_hash].revoked_at is None


async def test_refresh_replay_revokes_the_whole_token_family(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "refresh.replay@example.com"
    assert (await _register_user(client, email)).status_code == 201
    login = await _login(client, email)
    assert login.status_code == 200

    token_one = login.cookies["refresh_token"]

    rotation = await client.post(REFRESH_URL)
    assert rotation.status_code == 200
    token_two = _cookie_payload(_set_cookie_headers(rotation)["refresh_token"])
    assert token_two != token_one

    # Replay the already-rotated token the way an attacker holding it would.
    client.cookies.clear()
    replay = await client.post(
        REFRESH_URL,
        headers={"Cookie": f"refresh_token={token_one}"},
    )

    assert replay.status_code == 401
    assert replay.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"

    rows = await _refresh_rows(db_session_factory, email)
    assert _hash_token(token_two) in rows
    assert all(row.revoked_at is not None for row in rows.values())


async def test_refresh_rejects_missing_and_garbage_tokens(client: AsyncClient) -> None:
    without_cookie = await client.post(REFRESH_URL)
    assert without_cookie.status_code == 401

    client.cookies.clear()
    garbage = await client.post(
        REFRESH_URL,
        headers={"Cookie": "refresh_token=garbage-token"},
    )

    assert garbage.status_code == 401
