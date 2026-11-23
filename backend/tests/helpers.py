"""Builders shared by the API tests."""

from typing import Any

PASSWORD = "secret123"


def registration_payload(email: str, **overrides: Any) -> dict[str, Any]:
    """Return a valid registration body for ``email``.

    Usernames are unique in the database and several tests register more than
    one account, so the default username is derived from the email's local part.
    """
    payload: dict[str, Any] = {
        "email": email,
        "password": PASSWORD,
        "username": email.split("@", 1)[0].replace(".", "_"),
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "09120000000",
    }
    payload.update(overrides)
    return payload
