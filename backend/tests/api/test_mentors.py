"""Integration tests for mentor collaboration (F-035).

Every case drives the public API. Accounts are promoted to ``mentor`` in the
database because registration never assigns privileged roles (ADR-0006).
"""

import uuid
from typing import Any

from helpers import PASSWORD, registration_payload
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.models import MentorProfile, User

MENTORS_URL = "/api/v1/mentors"
SELECTED_URL = "/api/v1/mentors/selected"
CLIENTS_URL = "/api/v1/mentors/me/clients"
MESSAGES_URL = "/api/v1/mentor-messages"
PROGRAMS_URL = "/api/v1/mentor-programs"
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"
ROUTINES_URL = "/api/v1/routines"


async def _register(client: AsyncClient, email: str, **overrides: Any) -> None:
    response = await client.post(
        REGISTER_URL, json=registration_payload(email, **overrides)
    )
    assert response.status_code == 201, response.text


async def _login(client: AsyncClient, email: str) -> None:
    response = await client.post(
        LOGIN_URL, json={"identifier": email, "password": PASSWORD}
    )
    assert response.status_code == 200, response.text


async def _me(client: AsyncClient) -> dict[str, Any]:
    response = await client.get(ME_URL)
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body


async def _make_mentor(
    factory: async_sessionmaker[AsyncSession],
    email: str,
    headline: str = "مشاور برنامه‌ریزی",
) -> None:
    async with factory() as session:
        user = await session.scalar(select(User).where(User.email == email))
        assert user is not None
        user.role = "mentor"
        session.add(MentorProfile(user_id=user.id, headline=headline, bio="سابقه"))
        await session.commit()


async def _select(client: AsyncClient, mentor_id: str) -> None:
    response = await client.put(SELECTED_URL, json={"mentor_id": mentor_id})
    assert response.status_code == 200, response.text


async def _mentor_id(client: AsyncClient, email: str) -> str:
    """Return the id of a registered mentor by logging in as them."""
    await _login(client, email)
    return str((await _me(client))["id"])


async def test_mentor_endpoints_require_authentication(client: AsyncClient) -> None:
    program_id = uuid.uuid4()

    responses = [
        await client.get(MENTORS_URL),
        await client.get(SELECTED_URL),
        await client.put(SELECTED_URL, json={"mentor_id": str(uuid.uuid4())}),
        await client.delete(SELECTED_URL),
        await client.get(CLIENTS_URL),
        await client.get(MESSAGES_URL),
        await client.post(MESSAGES_URL, json={"body": "سلام"}),
        await client.get(PROGRAMS_URL),
        await client.post(
            PROGRAMS_URL,
            json={"client_id": str(uuid.uuid4()), "title": "x", "category": "study"},
        ),
        await client.post(f"{PROGRAMS_URL}/{program_id}/adopt"),
    ]

    for response in responses:
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_directory_lists_only_mentors_without_contact_details(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "mentor@example.com", first_name="مریم", last_name="کریمی")
    await _make_mentor(db_session_factory, "mentor@example.com", headline="برنامه درسی")
    await _register(client, "student@example.com")
    await _login(client, "student@example.com")

    directory = await client.get(MENTORS_URL)

    assert directory.status_code == 200
    body = directory.json()
    assert body["total"] == 1
    mentor = body["items"][0]
    assert mentor["name"] == "مریم کریمی"
    assert mentor["headline"] == "برنامه درسی"
    assert "email" not in mentor
    assert "phone_number" not in mentor


async def test_selecting_switching_and_revoking_one_mentor(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "student@example.com")
    await _register(client, "mentor-a@example.com", first_name="مربی", last_name="اول")
    await _register(client, "mentor-b@example.com", first_name="مربی", last_name="دوم")
    await _make_mentor(db_session_factory, "mentor-a@example.com")
    await _make_mentor(db_session_factory, "mentor-b@example.com")

    mentor_a = await _mentor_id(client, "mentor-a@example.com")
    mentor_b = await _mentor_id(client, "mentor-b@example.com")

    await _login(client, "student@example.com")
    student = str((await _me(client))["id"])

    assert (await client.get(SELECTED_URL)).json()["mentor"] is None

    await _select(client, mentor_a)
    selected = (await client.get(SELECTED_URL)).json()["mentor"]
    assert selected["id"] == mentor_a

    # Re-selecting is idempotent and keeps exactly one client row.
    await _select(client, mentor_a)

    await _login(client, "mentor-a@example.com")
    clients = (await client.get(CLIENTS_URL)).json()
    assert clients["total"] == 1
    assert clients["items"][0]["id"] == student

    await _login(client, "student@example.com")
    await _select(client, mentor_b)

    await _login(client, "mentor-a@example.com")
    assert (await client.get(CLIENTS_URL)).json()["total"] == 0

    await _login(client, "mentor-b@example.com")
    assert (await client.get(CLIENTS_URL)).json()["total"] == 1

    await _login(client, "student@example.com")
    cleared = await client.delete(SELECTED_URL)
    assert cleared.status_code == 204
    assert (await client.get(SELECTED_URL)).json()["mentor"] is None

    await _login(client, "mentor-b@example.com")
    assert (await client.get(CLIENTS_URL)).json()["total"] == 0


async def test_selecting_a_non_mentor_is_not_found(client: AsyncClient) -> None:
    await _register(client, "student@example.com")
    await _register(client, "plain@example.com")
    await _login(client, "plain@example.com")
    plain_id = str((await _me(client))["id"])

    await _login(client, "student@example.com")
    response = await client.put(SELECTED_URL, json={"mentor_id": plain_id})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "MENTOR_NOT_FOUND"


async def test_two_sided_chat_and_revocation_blocks_access(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "student@example.com")
    await _register(client, "mentor@example.com", first_name="مریم", last_name="کریمی")
    await _make_mentor(db_session_factory, "mentor@example.com")

    mentor_id = await _mentor_id(client, "mentor@example.com")
    await _login(client, "student@example.com")
    student_id = str((await _me(client))["id"])
    await _select(client, mentor_id)

    sent = await client.post(
        MESSAGES_URL, json={"mentor_id": mentor_id, "body": "  سلام  "}
    )
    assert sent.status_code == 201, sent.text
    assert sent.json()["body"] == "سلام"
    assert sent.json()["sender_id"] == student_id

    await _login(client, "mentor@example.com")
    thread = await client.get(MESSAGES_URL, params={"client_id": student_id})
    assert thread.status_code == 200
    assert thread.json()["total"] == 1

    reply = await client.post(
        MESSAGES_URL, json={"client_id": student_id, "body": "سلام، در خدمتم."}
    )
    assert reply.status_code == 201, reply.text
    assert reply.json()["sender_id"] == mentor_id

    await _login(client, "student@example.com")
    thread = await client.get(MESSAGES_URL, params={"mentor_id": mentor_id})
    assert [item["body"] for item in thread.json()["items"]] == [
        "سلام",
        "سلام، در خدمتم.",
    ]

    # A second user has an independent thread with the same mentor.
    await _register(client, "other@example.com")
    await _login(client, "other@example.com")
    await _select(client, mentor_id)
    own_thread = await client.get(MESSAGES_URL, params={"mentor_id": mentor_id})
    assert own_thread.json()["total"] == 0

    # Revocation takes effect on the very next request, in both directions.
    await _login(client, "student@example.com")
    await client.delete(SELECTED_URL)

    blocked_read = await client.get(MESSAGES_URL, params={"mentor_id": mentor_id})
    blocked_write = await client.post(
        MESSAGES_URL, json={"mentor_id": mentor_id, "body": "هنوز هستی؟"}
    )
    assert blocked_read.status_code == 403
    assert blocked_read.json()["error"]["code"] == "MENTOR_ACCESS_DENIED"
    assert blocked_write.status_code == 403

    await _login(client, "mentor@example.com")
    clients = (await client.get(CLIENTS_URL)).json()
    assert [client["id"] for client in clients["items"]] != [student_id]
    denied = await client.get(MESSAGES_URL, params={"client_id": student_id})
    assert denied.status_code == 403


async def test_programs_are_sent_by_mentor_and_adopted_once(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "student@example.com")
    await _register(client, "mentor@example.com", first_name="مریم", last_name="کریمی")
    await _make_mentor(db_session_factory, "mentor@example.com")

    mentor_id = await _mentor_id(client, "mentor@example.com")
    await _login(client, "student@example.com")
    student_id = str((await _me(client))["id"])
    await _select(client, mentor_id)

    # Users cannot create programs or list mentor clients.
    assert (await client.post(
        PROGRAMS_URL,
        json={"client_id": student_id, "title": "x", "category": "study"},
    )).status_code == 403
    assert (await client.get(CLIENTS_URL)).status_code == 403
    assert (await client.get(PROGRAMS_URL)).json()["total"] == 0

    await _login(client, "mentor@example.com")
    created = await client.post(
        PROGRAMS_URL,
        json={
            "client_id": student_id,
            "title": "  برنامه درسی دو هفته‌ای  ",
            "description": "روزی دو ساعت مطالعه",
            "category": "study",
        },
    )
    assert created.status_code == 201, created.text
    program = created.json()
    assert program["title"] == "برنامه درسی دو هفته‌ای"
    assert program["routine_id"] is None

    mentor_programs = await client.get(PROGRAMS_URL, params={"client_id": student_id})
    assert mentor_programs.json()["total"] == 1

    await _login(client, "student@example.com")
    programs = (await client.get(PROGRAMS_URL)).json()
    assert programs["total"] == 1
    assert programs["items"][0]["category"] == "study"

    adopted = await client.post(f"{PROGRAMS_URL}/{program['id']}/adopt")
    assert adopted.status_code == 200, adopted.text
    assert adopted.json()["routine_id"] is not None

    routines = (await client.get(ROUTINES_URL)).json()
    assert [routine["title"] for routine in routines["items"]] == [
        "برنامه درسی دو هفته‌ای"
    ]

    second = await client.post(f"{PROGRAMS_URL}/{program['id']}/adopt")
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "PROGRAM_ALREADY_ADOPTED"

    # Another user cannot adopt or list this program.
    await _register(client, "other@example.com")
    await _login(client, "other@example.com")
    assert (await client.get(PROGRAMS_URL)).json()["total"] == 0
    foreign = await client.post(f"{PROGRAMS_URL}/{program['id']}/adopt")
    assert foreign.status_code == 404
    assert foreign.json()["error"]["code"] == "MENTOR_PROGRAM_NOT_FOUND"


async def test_validation_and_consent_requirements(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "student@example.com")
    await _register(client, "mentor@example.com", first_name="مریم", last_name="کریمی")
    await _make_mentor(db_session_factory, "mentor@example.com")

    mentor_id = await _mentor_id(client, "mentor@example.com")
    await _login(client, "student@example.com")
    student_id = str((await _me(client))["id"])
    await _select(client, mentor_id)

    blank_message = await client.post(
        MESSAGES_URL, json={"mentor_id": mentor_id, "body": "   "}
    )
    missing_pair = await client.post(MESSAGES_URL, json={"body": "سلام"})
    assert blank_message.status_code == 422
    assert missing_pair.status_code == 422
    assert missing_pair.json()["error"]["code"] == "VALIDATION_ERROR"

    await _login(client, "mentor@example.com")
    blank_title = await client.post(
        PROGRAMS_URL,
        json={"client_id": student_id, "title": "  ", "category": "study"},
    )
    bad_category = await client.post(
        PROGRAMS_URL,
        json={"client_id": student_id, "title": "برنامه", "category": "music"},
    )
    # A client who never granted consent is refused.
    await _register(client, "stranger@example.com")
    stranger_id = str((await _me(client))["id"])
    await _login(client, "mentor@example.com")
    no_grant = await client.post(
        PROGRAMS_URL,
        json={"client_id": stranger_id, "title": "برنامه", "category": "life"},
    )

    for response in (blank_title, bad_category):
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert no_grant.status_code == 403
    assert no_grant.json()["error"]["code"] == "MENTOR_ACCESS_DENIED"
