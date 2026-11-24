"""Tests for the mocked forgot-password endpoint.

The reset flow itself is deferred (F-022); this endpoint only has to exist for
the redesigned login screen and must not reveal whether an account exists.
"""

import pytest
from helpers import registration_payload
from httpx import AsyncClient

FORGOT_URL = "/api/v1/auth/forgot-password"
REGISTER_URL = "/api/v1/auth/register"

RESPONSE = {"message": "Reset link sent"}


async def test_forgot_password_answers_identically_for_known_and_unknown_emails(
    client: AsyncClient,
) -> None:
    known = "known@example.com"
    assert (
        await client.post(REGISTER_URL, json=registration_payload(known))
    ).status_code == 201

    for email in (known, "nobody@example.com"):
        response = await client.post(FORGOT_URL, json={"email": email})

        assert response.status_code == 200
        assert response.json() == RESPONSE


@pytest.mark.parametrize("payload", [{}, {"email": ""}, {"email": "not-an-email"}])
async def test_forgot_password_rejects_a_missing_or_invalid_email(
    client: AsyncClient, payload: dict[str, str]
) -> None:
    response = await client.post(FORGOT_URL, json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
