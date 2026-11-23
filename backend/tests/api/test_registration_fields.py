"""Registration now captures the profile fields shown on the redesigned form.

The four new fields are required for *new* registrations while remaining
nullable in the database so pre-existing accounts keep working.
"""

import pytest
from helpers import PASSWORD, registration_payload
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"

PROFILE = {
    "username": "sara_ahmadi",
    "first_name": "سارا",
    "last_name": "احمدی",
    "phone_number": "09121234567",
}


@pytest.mark.parametrize(
    "missing", ["username", "first_name", "last_name", "phone_number"]
)
async def test_registration_requires_each_profile_field(
    client: AsyncClient, missing: str
) -> None:
    payload = registration_payload("incomplete@example.com")
    payload.pop(missing)

    response = await client.post(REGISTER_URL, json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_registration_stores_and_returns_the_profile(
    client: AsyncClient,
) -> None:
    payload = registration_payload("sara@example.com", **PROFILE)

    created = await client.post(REGISTER_URL, json=payload)

    assert created.status_code == 201, created.text
    body = created.json()
    for key, value in PROFILE.items():
        assert body[key] == value
    assert "password_hash" not in body

    login = await client.post(
        LOGIN_URL, json={"email": "sara@example.com", "password": PASSWORD}
    )
    assert login.status_code == 200

    me = (await client.get(ME_URL)).json()
    for key, value in PROFILE.items():
        assert me[key] == value
    assert me["email"] == "sara@example.com"


async def test_username_must_be_unique(client: AsyncClient) -> None:
    first = await client.post(
        REGISTER_URL,
        json=registration_payload("first@example.com", username="taken_name"),
    )
    second = await client.post(
        REGISTER_URL,
        json=registration_payload("second@example.com", username="taken_name"),
    )

    assert first.status_code == 201
    assert second.status_code == 400
    assert second.json()["error"]["code"] == "USERNAME_ALREADY_EXISTS"


async def test_profile_fields_are_trimmed(client: AsyncClient) -> None:
    payload = registration_payload(
        "spaced@example.com",
        username="  spaced_user  ",
        first_name="  Sara ",
        last_name=" Ahmadi  ",
        phone_number=" 0912 345 6789 ",
    )

    created = await client.post(REGISTER_URL, json=payload)

    assert created.status_code == 201, created.text
    body = created.json()
    assert body["username"] == "spaced_user"
    assert body["first_name"] == "Sara"
    assert body["last_name"] == "Ahmadi"
    assert body["phone_number"] == "09123456789"
