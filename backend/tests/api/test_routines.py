"""Integration tests for routine CRUD and ownership (F-005).

Every test drives the public API. Ownership is asserted the way an attacker
would: by taking a routine id that belongs to somebody else and asking for it.
"""

import uuid
from typing import Any

from helpers import registration_payload
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.models import Routine

ROUTINES_URL = "/api/v1/routines"
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

PASSWORD = "secret123"


async def _register(client: AsyncClient, email: str) -> None:
    response = await client.post(REGISTER_URL, json=registration_payload(email))
    assert response.status_code == 201, response.text


async def _login(client: AsyncClient, email: str) -> None:
    response = await client.post(LOGIN_URL, json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text


async def _create(
    client: AsyncClient, title: str, description: str | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"title": title}
    if description is not None:
        payload["description"] = description

    response = await client.post(ROUTINES_URL, json=payload)
    assert response.status_code == 201, response.text

    body: dict[str, Any] = response.json()
    return body


async def test_routine_endpoints_require_authentication(client: AsyncClient) -> None:
    routine_id = uuid.uuid4()

    responses = [
        await client.post(ROUTINES_URL, json={"title": "Run"}),
        await client.get(ROUTINES_URL),
        await client.get(f"{ROUTINES_URL}/{routine_id}"),
        await client.put(f"{ROUTINES_URL}/{routine_id}", json={"title": "Run"}),
        await client.delete(f"{ROUTINES_URL}/{routine_id}"),
    ]

    for response in responses:
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_create_returns_the_new_routine(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _login(client, "owner@example.com")

    response = await client.post(
        ROUTINES_URL, json={"title": "Morning run", "description": "5 km"}
    )

    assert response.status_code == 201
    body = response.json()
    # The owner is implied by the session, and the payload must not leak
    # internal columns such as `user_id` or `deleted_at`.
    assert set(body) == {
        "id",
        "title",
        "description",
        "is_active",
        "created_at",
        "updated_at",
    }
    assert body["title"] == "Morning run"
    assert body["description"] == "5 km"
    assert body["is_active"] is True
    uuid.UUID(body["id"])


async def test_create_accepts_a_routine_without_a_description(
    client: AsyncClient,
) -> None:
    await _register(client, "owner@example.com")
    await _login(client, "owner@example.com")

    response = await client.post(ROUTINES_URL, json={"title": "Read"})

    assert response.status_code == 201
    assert response.json()["description"] is None


async def test_create_rejects_a_blank_or_missing_title(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _login(client, "owner@example.com")

    blank = await client.post(ROUTINES_URL, json={"title": "   "})
    missing = await client.post(ROUTINES_URL, json={"description": "no title"})

    assert blank.status_code == 422
    assert blank.json()["error"]["code"] == "VALIDATION_ERROR"
    assert missing.status_code == 422
    assert missing.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_list_returns_only_the_callers_routines(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _register(client, "other@example.com")

    await _login(client, "owner@example.com")
    await _create(client, "Owner one")
    await _create(client, "Owner two")

    await _login(client, "other@example.com")
    await _create(client, "Other one")

    other_list = await client.get(ROUTINES_URL)
    assert other_list.status_code == 200
    assert other_list.json()["total"] == 1
    assert [item["title"] for item in other_list.json()["items"]] == ["Other one"]

    await _login(client, "owner@example.com")
    owner_list = await client.get(ROUTINES_URL)

    assert owner_list.status_code == 200
    assert owner_list.json()["total"] == 2
    assert {item["title"] for item in owner_list.json()["items"]} == {
        "Owner one",
        "Owner two",
    }


async def test_get_returns_an_owned_routine(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _login(client, "owner@example.com")
    created = await _create(client, "Morning run", "5 km")

    response = await client.get(f"{ROUTINES_URL}/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["title"] == "Morning run"


async def test_get_another_users_routine_is_not_found(client: AsyncClient) -> None:
    """A foreign id answers 404 rather than 403, so existence is not leaked."""
    await _register(client, "owner@example.com")
    await _register(client, "intruder@example.com")

    await _login(client, "owner@example.com")
    created = await _create(client, "Private routine", "Not yours")

    await _login(client, "intruder@example.com")
    response = await client.get(f"{ROUTINES_URL}/{created['id']}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ROUTINE_NOT_FOUND"


async def test_update_changes_title_and_description(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _login(client, "owner@example.com")
    created = await _create(client, "Morning run", "5 km")

    response = await client.put(
        f"{ROUTINES_URL}/{created['id']}",
        json={"title": "Evening run", "description": "10 km"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Evening run"
    assert response.json()["description"] == "10 km"

    persisted = await client.get(f"{ROUTINES_URL}/{created['id']}")
    assert persisted.json()["title"] == "Evening run"
    assert persisted.json()["description"] == "10 km"


async def test_update_can_change_only_the_description(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _login(client, "owner@example.com")
    created = await _create(client, "Morning run", "5 km")

    response = await client.put(
        f"{ROUTINES_URL}/{created['id']}", json={"description": "8 km"}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Morning run"
    assert response.json()["description"] == "8 km"


async def test_update_rejects_an_empty_payload(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _login(client, "owner@example.com")
    created = await _create(client, "Morning run")

    response = await client.put(f"{ROUTINES_URL}/{created['id']}", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_update_another_users_routine_is_not_found(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _register(client, "intruder@example.com")

    await _login(client, "owner@example.com")
    created = await _create(client, "Private routine")

    await _login(client, "intruder@example.com")
    response = await client.put(
        f"{ROUTINES_URL}/{created['id']}", json={"title": "Hijacked"}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ROUTINE_NOT_FOUND"

    await _login(client, "owner@example.com")
    unchanged = await client.get(f"{ROUTINES_URL}/{created['id']}")
    assert unchanged.json()["title"] == "Private routine"


async def test_delete_soft_deletes_and_returns_204(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "owner@example.com")
    await _login(client, "owner@example.com")
    created = await _create(client, "Morning run")
    routine_id = uuid.UUID(created["id"])

    response = await client.delete(f"{ROUTINES_URL}/{routine_id}")

    assert response.status_code == 204
    assert response.content == b""

    listed = await client.get(ROUTINES_URL)
    assert listed.json()["total"] == 0

    fetched = await client.get(f"{ROUTINES_URL}/{routine_id}")
    assert fetched.status_code == 404

    # The row survives for history; only its visibility changed.
    async with db_session_factory() as session:
        row = await session.get(Routine, routine_id)

    assert row is not None
    assert row.deleted_at is not None
    assert row.is_active is False


async def test_deleting_twice_is_not_found(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _login(client, "owner@example.com")
    created = await _create(client, "Morning run")

    first = await client.delete(f"{ROUTINES_URL}/{created['id']}")
    second = await client.delete(f"{ROUTINES_URL}/{created['id']}")

    assert first.status_code == 204
    assert second.status_code == 404
    assert second.json()["error"]["code"] == "ROUTINE_NOT_FOUND"


async def test_delete_another_users_routine_is_not_found(client: AsyncClient) -> None:
    await _register(client, "owner@example.com")
    await _register(client, "intruder@example.com")

    await _login(client, "owner@example.com")
    created = await _create(client, "Private routine")

    await _login(client, "intruder@example.com")
    response = await client.delete(f"{ROUTINES_URL}/{created['id']}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ROUTINE_NOT_FOUND"

    await _login(client, "owner@example.com")
    still_there = await client.get(f"{ROUTINES_URL}/{created['id']}")
    assert still_there.status_code == 200
