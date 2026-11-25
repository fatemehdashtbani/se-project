"""Integration tests for the personal tools: checklist, notes, calendar (F-033).

Like the routine tests, every case drives the public API and proves ownership by
asking for another account's id.
"""

import uuid
from typing import Any

from helpers import registration_payload
from httpx import AsyncClient

CHECKLIST_URL = "/api/v1/checklist-items"
NOTES_URL = "/api/v1/notes"
EVENTS_URL = "/api/v1/calendar-events"
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

PASSWORD = "secret123"


async def _register_and_login(client: AsyncClient, email: str) -> None:
    registered = await client.post(REGISTER_URL, json=registration_payload(email))
    assert registered.status_code == 201, registered.text

    logged_in = await client.post(
        LOGIN_URL, json={"identifier": email, "password": PASSWORD}
    )
    assert logged_in.status_code == 200, logged_in.text


async def _create(client: AsyncClient, url: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = await client.post(url, json=payload)
    assert response.status_code == 201, response.text

    body: dict[str, Any] = response.json()
    return body


async def test_personal_endpoints_require_authentication(client: AsyncClient) -> None:
    item_id = uuid.uuid4()

    responses = [
        await client.get(CHECKLIST_URL),
        await client.post(CHECKLIST_URL, json={"title": "Read"}),
        await client.put(f"{CHECKLIST_URL}/{item_id}", json={"is_done": True}),
        await client.delete(f"{CHECKLIST_URL}/{item_id}"),
        await client.get(NOTES_URL),
        await client.post(NOTES_URL, json={"title": "Idea"}),
        await client.put(f"{NOTES_URL}/{item_id}", json={"title": "Edited"}),
        await client.delete(f"{NOTES_URL}/{item_id}"),
        await client.get(EVENTS_URL),
        await client.post(EVENTS_URL, json={"title": "Meet", "event_date": "2026-12-01"}),
        await client.delete(f"{EVENTS_URL}/{item_id}"),
    ]

    for response in responses:
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_checklist_item_lifecycle(client: AsyncClient) -> None:
    await _register_and_login(client, "owner@example.com")

    created = await _create(client, CHECKLIST_URL, {"title": "  خرید نان  "})
    assert set(created) == {"id", "title", "is_done", "created_at", "updated_at"}
    assert created["title"] == "خرید نان"
    assert created["is_done"] is False

    listed = await client.get(CHECKLIST_URL)
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["done"] == 0

    ticked = await client.put(
        f"{CHECKLIST_URL}/{created['id']}", json={"is_done": True}
    )
    assert ticked.status_code == 200
    assert ticked.json()["is_done"] is True

    counters = await client.get(CHECKLIST_URL)
    assert counters.json()["done"] == 1

    renamed = await client.put(
        f"{CHECKLIST_URL}/{created['id']}", json={"title": "خرید میوه"}
    )
    assert renamed.json()["title"] == "خرید میوه"
    assert renamed.json()["is_done"] is True

    deleted = await client.delete(f"{CHECKLIST_URL}/{created['id']}")
    assert deleted.status_code == 204
    assert (await client.get(CHECKLIST_URL)).json()["total"] == 0


async def test_checklist_rejects_blank_titles_and_empty_updates(
    client: AsyncClient,
) -> None:
    await _register_and_login(client, "owner@example.com")

    blank = await client.post(CHECKLIST_URL, json={"title": "   "})
    missing = await client.post(CHECKLIST_URL, json={})
    assert blank.status_code == 422
    assert missing.status_code == 422

    created = await _create(client, CHECKLIST_URL, {"title": "Read"})
    empty = await client.put(f"{CHECKLIST_URL}/{created['id']}", json={})
    assert empty.status_code == 422
    assert empty.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_checklist_does_not_expose_another_users_item(client: AsyncClient) -> None:
    await _register_and_login(client, "owner@example.com")
    created = await _create(client, CHECKLIST_URL, {"title": "Private"})

    await _register_and_login(client, "intruder@example.com")

    updated = await client.put(f"{CHECKLIST_URL}/{created['id']}", json={"is_done": True})
    deleted = await client.delete(f"{CHECKLIST_URL}/{created['id']}")

    assert updated.status_code == 404
    assert updated.json()["error"]["code"] == "CHECKLIST_ITEM_NOT_FOUND"
    assert deleted.status_code == 404


async def test_notes_lifecycle(client: AsyncClient) -> None:
    await _register_and_login(client, "owner@example.com")

    created = await _create(
        client, NOTES_URL, {"title": "  ایده  ", "content": "  متن اولیه  "}
    )
    assert set(created) == {"id", "title", "content", "created_at", "updated_at"}
    assert created["title"] == "ایده"
    assert created["content"] == "متن اولیه"

    listed = await client.get(NOTES_URL)
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    updated = await client.put(
        f"{NOTES_URL}/{created['id']}",
        json={"title": "ایده جدید", "content": "متن دوم"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "ایده جدید"
    assert updated.json()["content"] == "متن دوم"

    partial = await client.put(f"{NOTES_URL}/{created['id']}", json={"content": "فقط متن"})
    assert partial.json()["title"] == "ایده جدید"
    assert partial.json()["content"] == "فقط متن"

    deleted = await client.delete(f"{NOTES_URL}/{created['id']}")
    assert deleted.status_code == 204
    assert (await client.get(NOTES_URL)).json()["total"] == 0


async def test_notes_reject_blank_titles_and_empty_updates(client: AsyncClient) -> None:
    await _register_and_login(client, "owner@example.com")

    assert (await client.post(NOTES_URL, json={"title": "   "})).status_code == 422

    created = await _create(client, NOTES_URL, {"title": "یادداشت"})
    empty = await client.put(f"{NOTES_URL}/{created['id']}", json={})
    assert empty.status_code == 422
    assert empty.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_notes_do_not_expose_another_users_note(client: AsyncClient) -> None:
    await _register_and_login(client, "owner@example.com")
    created = await _create(client, NOTES_URL, {"title": "Private"})

    await _register_and_login(client, "intruder@example.com")

    updated = await client.put(f"{NOTES_URL}/{created['id']}", json={"title": "Mine now"})
    deleted = await client.delete(f"{NOTES_URL}/{created['id']}")

    assert updated.status_code == 404
    assert updated.json()["error"]["code"] == "NOTE_NOT_FOUND"
    assert deleted.status_code == 404


async def test_calendar_events_lifecycle_and_window_filter(client: AsyncClient) -> None:
    await _register_and_login(client, "owner@example.com")

    december = await _create(
        client, EVENTS_URL, {"title": "  جلسه  ", "event_date": "2026-12-10"}
    )
    assert set(december) == {"id", "title", "event_date", "created_at"}
    assert december["title"] == "جلسه"
    assert december["event_date"] == "2026-12-10"

    january = await _create(
        client, EVENTS_URL, {"title": "سال نو", "event_date": "2027-01-01"}
    )

    all_events = await client.get(EVENTS_URL)
    assert all_events.json()["total"] == 2

    window = await client.get(
        EVENTS_URL, params={"start": "2026-12-01", "end": "2026-12-31"}
    )
    assert window.status_code == 200
    assert window.json()["total"] == 1
    assert window.json()["items"][0]["id"] == december["id"]

    deleted = await client.delete(f"{EVENTS_URL}/{january['id']}")
    assert deleted.status_code == 204
    remaining = await client.get(EVENTS_URL)
    assert remaining.json()["total"] == 1
    assert remaining.json()["items"][0]["id"] == december["id"]


async def test_calendar_rejects_invalid_payloads(client: AsyncClient) -> None:
    await _register_and_login(client, "owner@example.com")

    blank = await client.post(EVENTS_URL, json={"title": "  ", "event_date": "2026-12-01"})
    missing_date = await client.post(EVENTS_URL, json={"title": "Meet"})
    bad_date = await client.post(EVENTS_URL, json={"title": "Meet", "event_date": "not-a-date"})

    for response in (blank, missing_date, bad_date):
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_calendar_does_not_expose_another_users_event(client: AsyncClient) -> None:
    await _register_and_login(client, "owner@example.com")
    created = await _create(
        client, EVENTS_URL, {"title": "Private", "event_date": "2026-12-01"}
    )

    await _register_and_login(client, "intruder@example.com")

    deleted = await client.delete(f"{EVENTS_URL}/{created['id']}")

    assert deleted.status_code == 404
    assert deleted.json()["error"]["code"] == "CALENDAR_EVENT_NOT_FOUND"
