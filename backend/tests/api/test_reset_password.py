"""Integration tests for ``POST /api/v1/auth/reset-password`` (F-022)."""

from datetime import UTC, datetime, timedelta

from helpers import registration_payload
from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.dependencies import get_email_sender
from app.infrastructure.db.models import PasswordResetToken
from app.infrastructure.email import EmailContent
from app.main import app

from .test_forgot_password import FORGOT_URL, FakeSender, _token_from

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
RESET_URL = "/api/v1/auth/reset-password"
REFRESH_URL = "/api/v1/auth/refresh"

PASSWORD = "secret123"
NEW_PASSWORD = "brand-new-9876"


async def _request_token(client: AsyncClient, email: str) -> str:
    sent: list[tuple[str, EmailContent]] = []
    app.dependency_overrides[get_email_sender] = lambda: FakeSender(sent)

    assert (
        await client.post(REGISTER_URL, json=registration_payload(email))
    ).status_code == 201
    assert (await client.post(FORGOT_URL, json={"email": email})).status_code == 200

    assert len(sent) == 1
    return _token_from(sent[0][1])


async def test_reset_password_sets_the_new_password_and_single_uses_the_token(
    client: AsyncClient,
) -> None:
    email = "reset.flow@example.com"
    token = await _request_token(client, email)

    response = await client.post(
        RESET_URL, json={"token": token, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 200

    client.cookies.clear()
    old_login = await client.post(
        LOGIN_URL, json={"identifier": email, "password": PASSWORD}
    )
    assert old_login.status_code == 401

    new_login = await client.post(
        LOGIN_URL, json={"identifier": email, "password": NEW_PASSWORD}
    )
    assert new_login.status_code == 200

    client.cookies.clear()
    replay = await client.post(
        RESET_URL, json={"token": token, "new_password": "another-one-1234"}
    )
    assert replay.status_code == 400
    assert replay.json()["error"]["code"] == "INVALID_RESET_TOKEN"


async def test_reset_password_rejects_an_unknown_token(client: AsyncClient) -> None:
    response = await client.post(
        RESET_URL, json={"token": "never-issued", "new_password": NEW_PASSWORD}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_RESET_TOKEN"


async def test_reset_password_rejects_an_expired_token(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    token = await _request_token(client, "reset.expired@example.com")

    async with db_session_factory() as session:
        await session.execute(
            update(PasswordResetToken).values(
                expires_at=datetime.now(UTC) - timedelta(minutes=1)
            )
        )
        await session.commit()

    response = await client.post(
        RESET_URL, json={"token": token, "new_password": NEW_PASSWORD}
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_RESET_TOKEN"


async def test_reset_password_ends_existing_sessions(client: AsyncClient) -> None:
    email = "reset.sessions@example.com"
    token = await _request_token(client, email)

    assert (
        await client.post(
            LOGIN_URL, json={"identifier": email, "password": PASSWORD}
        )
    ).status_code == 200

    response = await client.post(
        RESET_URL, json={"token": token, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 200

    assert (await client.post(REFRESH_URL)).status_code == 401


async def test_reset_password_validates_the_payload(client: AsyncClient) -> None:
    for payload in (
        {},
        {"token": "", "new_password": NEW_PASSWORD},
        {"token": "anything", "new_password": "short"},
    ):
        response = await client.post(RESET_URL, json=payload)

        assert response.status_code == 422, payload
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_reset_password_invalidates_other_outstanding_tokens(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "reset.other-tokens@example.com"
    first = await _request_token(client, email)

    # A second link can be issued after the cooldown; consuming the first must
    # invalidate the second as well.
    async with db_session_factory() as session:
        await session.execute(
            update(PasswordResetToken).values(
                created_at=datetime.now(UTC) - timedelta(minutes=5)
            )
        )
        await session.commit()

    sent: list[tuple[str, EmailContent]] = []
    app.dependency_overrides[get_email_sender] = lambda: FakeSender(sent)
    assert (await client.post(FORGOT_URL, json={"email": email})).status_code == 200
    second = _token_from(sent[0][1])

    assert (
        await client.post(
            RESET_URL, json={"token": first, "new_password": NEW_PASSWORD}
        )
    ).status_code == 200

    replay = await client.post(
        RESET_URL, json={"token": second, "new_password": "another-one-1234"}
    )
    assert replay.status_code == 400

    async with db_session_factory() as session:
        rows = (await session.scalars(select(PasswordResetToken))).all()
    assert all(row.used_at is not None for row in rows)
