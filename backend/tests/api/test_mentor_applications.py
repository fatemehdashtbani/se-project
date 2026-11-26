"""Integration tests for mentor applications (F-036).

A regular user submits expertise, biography and evidence; the request waits as
``pending`` until an administrator approves (role becomes ``mentor`` and a
public profile is published) or rejects it.
"""

import uuid
from typing import Any

from helpers import PASSWORD, registration_payload
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.models import User

APPLICATIONS_URL = "/api/v1/mentor-applications"
MY_APPLICATION_URL = f"{APPLICATIONS_URL}/me"
ADMIN_URL = "/api/v1/admin/mentor-applications"
MENTORS_URL = "/api/v1/mentors"
ME_URL = "/api/v1/auth/me"
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"


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


async def _promote_admin(
    factory: async_sessionmaker[AsyncSession], email: str
) -> None:
    async with factory() as session:
        user = await session.scalar(select(User).where(User.email == email))
        assert user is not None
        user.role = "admin"
        await session.commit()


def _application_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "expertise": "برنامه‌ریزی درسی و مطالعه",
        "bio": "ده سال تجربه مشاوره تحصیلی.",
        "documents": "https://example.com/certificate",
    }
    payload.update(overrides)
    return payload


async def test_application_endpoints_require_authentication(
    client: AsyncClient,
) -> None:
    responses = [
        await client.get(MY_APPLICATION_URL),
        await client.post(APPLICATIONS_URL, json=_application_payload()),
        await client.get(ADMIN_URL),
        await client.post(f"{ADMIN_URL}/{uuid.uuid4()}/approve"),
        await client.post(f"{ADMIN_URL}/{uuid.uuid4()}/reject"),
    ]

    for response in responses:
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_user_submits_a_pending_application_and_resubmits_in_place(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "candidate@example.com", first_name="سارا", last_name="احمدی")
    await _login(client, "candidate@example.com")

    empty = await client.get(MY_APPLICATION_URL)
    assert empty.status_code == 200
    assert empty.json()["application"] is None

    created = await client.post(
        APPLICATIONS_URL,
        json=_application_payload(
            expertise="  برنامه‌ریزی درسی  ",
            bio="  ده سال تجربه مشاوره تحصیلی.  ",
            documents="  ",
        ),
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["expertise"] == "برنامه‌ریزی درسی"
    assert body["bio"] == "ده سال تجربه مشاوره تحصیلی."
    assert body["documents"] is None
    assert body["status"] == "pending"
    assert body["reviewed_at"] is None

    mine = await client.get(MY_APPLICATION_URL)
    assert mine.json()["application"]["id"] == body["id"]
    assert mine.json()["application"]["status"] == "pending"

    # A second submission updates the same row instead of queueing a duplicate.
    resubmitted = await client.post(
        APPLICATIONS_URL,
        json=_application_payload(expertise="مشاوره ورزشی"),
    )
    assert resubmitted.status_code == 201, resubmitted.text
    assert resubmitted.json()["id"] == body["id"]
    assert resubmitted.json()["expertise"] == "مشاوره ورزشی"

    await _register(client, "admin@example.com")
    await _promote_admin(db_session_factory, "admin@example.com")
    await _login(client, "admin@example.com")

    queue = await client.get(ADMIN_URL)
    assert queue.status_code == 200
    assert queue.json()["total"] == 1
    item = queue.json()["items"][0]
    assert item["applicant_name"] == "سارا احمدی"
    assert item["applicant_email"] == "candidate@example.com"
    assert item["expertise"] == "مشاوره ورزشی"


async def test_only_admin_can_review_and_approval_promotes_the_mentor(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "candidate@example.com", first_name="سارا", last_name="احمدی")
    await _register(client, "admin@example.com")
    await _promote_admin(db_session_factory, "admin@example.com")

    await _login(client, "candidate@example.com")
    application = (await client.post(APPLICATIONS_URL, json=_application_payload())).json()
    application_id = application["id"]

    forbidden_list = await client.get(ADMIN_URL)
    forbidden_approve = await client.post(f"{ADMIN_URL}/{application_id}/approve")
    forbidden_reject = await client.post(f"{ADMIN_URL}/{application_id}/reject")
    for response in (forbidden_list, forbidden_approve, forbidden_reject):
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN"

    await _login(client, "admin@example.com")
    approved = await client.post(f"{ADMIN_URL}/{application_id}/approve")
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"
    assert approved.json()["reviewed_at"] is not None

    await _login(client, "candidate@example.com")
    assert (await _me(client))["role"] == "mentor"

    directory = await client.get(MENTORS_URL)
    mentors = directory.json()["items"]
    assert [mentor["name"] for mentor in mentors] == ["سارا احمدی"]
    assert mentors[0]["headline"] == "برنامه‌ریزی درسی و مطالعه"
    assert mentors[0]["bio"] == "ده سال تجربه مشاوره تحصیلی."

    # A mentor cannot apply again, and the review cannot be repeated.
    again = await client.post(APPLICATIONS_URL, json=_application_payload())
    assert again.status_code == 403
    assert again.json()["error"]["code"] == "FORBIDDEN"

    await _login(client, "admin@example.com")
    duplicate = await client.post(f"{ADMIN_URL}/{application_id}/approve")
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "MENTOR_APPLICATION_NOT_PENDING"


async def test_rejection_keeps_the_user_role_and_allows_resubmission(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "candidate@example.com")
    await _register(client, "admin@example.com")
    await _promote_admin(db_session_factory, "admin@example.com")

    await _login(client, "candidate@example.com")
    application_id = (
        await client.post(APPLICATIONS_URL, json=_application_payload())
    ).json()["id"]

    await _login(client, "admin@example.com")
    rejected = await client.post(f"{ADMIN_URL}/{application_id}/reject")
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["status"] == "rejected"

    assert (await client.get(f"{ADMIN_URL}?status=rejected")).json()["total"] == 1
    assert (await client.get(f"{ADMIN_URL}?status=pending")).json()["total"] == 0
    bad_status = await client.get(f"{ADMIN_URL}?status=maybe")
    assert bad_status.status_code == 422

    await _login(client, "candidate@example.com")
    assert (await _me(client))["role"] == "user"
    mine = await client.get(MY_APPLICATION_URL)
    assert mine.json()["application"]["status"] == "rejected"

    resubmitted = await client.post(
        APPLICATIONS_URL,
        json=_application_payload(expertise="مشاوره شغلی"),
    )
    assert resubmitted.status_code == 201, resubmitted.text
    assert resubmitted.json()["id"] == application_id
    assert resubmitted.json()["status"] == "pending"
    assert resubmitted.json()["reviewed_at"] is None


async def test_validation_and_unknown_applications(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "candidate@example.com")
    await _register(client, "admin@example.com")
    await _promote_admin(db_session_factory, "admin@example.com")

    await _login(client, "candidate@example.com")
    blank_expertise = await client.post(
        APPLICATIONS_URL, json=_application_payload(expertise="   ")
    )
    blank_bio = await client.post(
        APPLICATIONS_URL, json=_application_payload(bio="   ")
    )
    too_long_expertise = await client.post(
        APPLICATIONS_URL, json=_application_payload(expertise="x" * 201)
    )

    for response in (blank_expertise, blank_bio, too_long_expertise):
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    await _login(client, "admin@example.com")
    missing = await client.post(f"{ADMIN_URL}/{uuid.uuid4()}/approve")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "MENTOR_APPLICATION_NOT_FOUND"
