"""Integration tests for emailed password-reset requests (F-022).

The endpoint must never reveal whether an address is registered, must send a
single-use link only when delivery actually works, and must not claim success
when the relay fails.
"""

import re
from collections.abc import Iterator

import pytest
from helpers import registration_payload
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.dependencies import get_email_sender
from app.infrastructure.db.models import PasswordResetToken, User
from app.infrastructure.email import EmailContent, EmailContent as _Content  # noqa: F401
from app.infrastructure.email import EmailDeliveryError
from app.main import app

FORGOT_URL = "/api/v1/auth/forgot-password"
REGISTER_URL = "/api/v1/auth/register"

RESPONSE = {"message": "Reset link sent"}
TOKEN_PATTERN = re.compile(r"token=([A-Za-z0-9_\-]+)")


class FakeSender:
    """Records outgoing mail instead of talking to SMTP."""

    def __init__(self, sent: list[tuple[str, EmailContent]]) -> None:
        self._sent = sent

    async def send(self, *, to: str, content: EmailContent) -> None:
        self._sent.append((to, content))


class FailingSender:
    """Simulates a relay that rejects the message."""

    async def send(self, *, to: str, content: EmailContent) -> None:
        raise EmailDeliveryError


@pytest.fixture
def sent_emails() -> Iterator[list[tuple[str, EmailContent]]]:
    """Override the email port with a recording fake for one test."""
    sent: list[tuple[str, EmailContent]] = []
    app.dependency_overrides[get_email_sender] = lambda: FakeSender(sent)
    yield sent


@pytest.fixture
def failing_email() -> Iterator[None]:
    """Override the email port with a sender that always fails."""
    app.dependency_overrides[get_email_sender] = lambda: FailingSender()
    yield None


async def _register(client: AsyncClient, email: str) -> None:
    assert (
        await client.post(REGISTER_URL, json=registration_payload(email))
    ).status_code == 201


def _token_from(email: EmailContent) -> str:
    match = TOKEN_PATTERN.search(email.text)
    assert match is not None, email.text
    return match.group(1)


async def test_forgot_password_emails_a_reset_link_to_a_registered_address(
    client: AsyncClient, sent_emails: list[tuple[str, EmailContent]]
) -> None:
    email = "reset.known@example.com"
    await _register(client, email)

    response = await client.post(FORGOT_URL, json={"email": email})

    assert response.status_code == 200
    assert response.json() == RESPONSE
    assert len(sent_emails) == 1

    recipient, content = sent_emails[0]
    assert recipient == email
    assert "بازیابی رمز عبور" in content.subject
    assert "/reset-password?token=" in content.text
    assert "/reset-password?token=" in content.html


async def test_forgot_password_answers_identically_for_unknown_and_known_emails(
    client: AsyncClient, sent_emails: list[tuple[str, EmailContent]]
) -> None:
    known = "reset.same-answer@example.com"
    await _register(client, known)

    known_response = await client.post(FORGOT_URL, json={"email": known})
    unknown_response = await client.post(
        FORGOT_URL, json={"email": "reset.nobody@example.com"}
    )

    assert known_response.status_code == unknown_response.status_code == 200
    assert known_response.json() == unknown_response.json() == RESPONSE
    assert [recipient for recipient, _ in sent_emails] == [known]


async def test_forgot_password_does_not_resend_within_the_cooldown(
    client: AsyncClient, sent_emails: list[tuple[str, EmailContent]]
) -> None:
    email = "reset.cooldown@example.com"
    await _register(client, email)

    first = await client.post(FORGOT_URL, json={"email": email})
    second = await client.post(FORGOT_URL, json={"email": email})

    assert first.json() == second.json() == RESPONSE
    assert len(sent_emails) == 1


async def test_forgot_password_reports_a_delivery_failure_instead_of_claiming_success(
    client: AsyncClient,
    failing_email: None,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "reset.broken-relay@example.com"
    await _register(client, email)

    response = await client.post(FORGOT_URL, json={"email": email})

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "EMAIL_DELIVERY_FAILED"

    # No usable token may survive an email that was never delivered.
    async with db_session_factory() as session:
        count = await session.scalar(select(func.count(PasswordResetToken.id)))
    assert count == 0


@pytest.mark.parametrize("payload", [{}, {"email": ""}, {"email": "not-an-email"}])
async def test_forgot_password_rejects_a_missing_or_invalid_email(
    client: AsyncClient, payload: dict[str, str]
) -> None:
    response = await client.post(FORGOT_URL, json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_reset_password_token_belongs_to_the_registered_account(
    client: AsyncClient,
    sent_emails: list[tuple[str, EmailContent]],
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "reset.owner@example.com"
    await _register(client, email)
    await client.post(FORGOT_URL, json={"email": email})

    token = _token_from(sent_emails[0][1])

    async with db_session_factory() as session:
        row = await session.scalar(select(PasswordResetToken))
        user = await session.scalar(select(User).where(User.email == email))

    assert row is not None and user is not None
    assert row.user_id == user.id
    assert row.token_hash != token
