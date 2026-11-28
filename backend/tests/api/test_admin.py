"""Integration tests for the admin panel API (F-037).

The panel is admin-only, every mutation is audited, and an account control
(ban/disable) takes effect at login and on the next authenticated request.
"""

from typing import Any

from helpers import PASSWORD, registration_payload
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.db.models import User

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"
DASHBOARD_URL = "/api/v1/admin/dashboard"
USERS_URL = "/api/v1/admin/users"
TEMPLATES_URL = "/api/v1/admin/templates"
CATEGORIES_URL = "/api/v1/admin/categories"
BROADCASTS_URL = "/api/v1/admin/broadcasts"
LOGS_URL = "/api/v1/admin/logs"


async def _register(client: AsyncClient, email: str, **overrides: Any) -> None:
    response = await client.post(
        REGISTER_URL, json=registration_payload(email, **overrides)
    )
    assert response.status_code == 201, response.text


async def _login(client: AsyncClient, email: str, password: str = PASSWORD) -> Any:
    return await client.post(
        LOGIN_URL, json={"identifier": email, "password": password}
    )


async def _promote_admin(
    factory: async_sessionmaker[AsyncSession], email: str
) -> None:
    async with factory() as session:
        user = await session.scalar(select(User).where(User.email == email))
        assert user is not None
        user.role = "admin"
        await session.commit()


async def _admin_client(
    client: AsyncClient, factory: async_sessionmaker[AsyncSession]
) -> None:
    await _register(client, "admin@example.com")
    await _promote_admin(factory, "admin@example.com")
    assert (await _login(client, "admin@example.com")).status_code == 200


async def test_admin_endpoints_reject_guests_and_non_admins(
    client: AsyncClient,
) -> None:
    guest = await client.get(DASHBOARD_URL)
    assert guest.status_code == 401
    assert guest.json()["error"]["code"] == "UNAUTHORIZED"

    await _register(client, "user@example.com")
    await _login(client, "user@example.com")

    for response in (
        await client.get(DASHBOARD_URL),
        await client.get(USERS_URL),
        await client.post(f"{USERS_URL}/anything/ban", json={"value": True}),
        await client.get(TEMPLATES_URL),
        await client.get(LOGS_URL),
    ):
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN"


async def test_dashboard_reports_platform_counters(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "first@example.com")
    await _register(client, "second@example.com")
    await _login(client, "first@example.com")
    await client.post(
        "/api/v1/routines", json={"title": "ورزش صبحگاهی", "description": None}
    )

    await _admin_client(client, db_session_factory)
    response = await client.get(DASHBOARD_URL)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total_users"] == 3
    assert body["total_routines"] == 1
    assert body["total_mentors"] == 0
    assert body["pending_mentor_requests"] == 0
    assert len(body["activity"]) == 14
    assert body["activity"][-1]["routines"] == 1


async def test_user_search_ban_and_activation_take_effect_immediately(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "sara@example.com", first_name="سارا")
    await _register(client, "reza@example.com", first_name="رضا")
    await _admin_client(client, db_session_factory)

    filtered = await client.get(f"{USERS_URL}?search=sara")
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    sara = filtered.json()["items"][0]
    assert sara["first_name"] == "سارا"
    assert sara["is_active"] is True
    assert sara["is_banned"] is False

    banned = await client.post(
        f"{USERS_URL}/{sara['id']}/ban", json={"value": True}
    )
    assert banned.status_code == 200, banned.text
    assert banned.json()["is_banned"] is True

    # The ban is enforced at login and does not reveal whether the password was right.
    rejected_login = await _login(client, "sara@example.com")
    assert rejected_login.status_code == 403
    assert rejected_login.json()["error"]["code"] == "ACCOUNT_DISABLED"

    banned_filter = await client.get(f"{USERS_URL}?status=banned")
    assert banned_filter.json()["total"] == 1

    await client.post(f"{USERS_URL}/{sara['id']}/ban", json={"value": False})
    disabled = await client.post(
        f"{USERS_URL}/{sara['id']}/activation", json={"value": False}
    )
    assert disabled.json()["is_active"] is False
    assert (await _login(client, "sara@example.com")).status_code == 403

    await client.post(f"{USERS_URL}/{sara['id']}/activation", json={"value": True})
    assert (await _login(client, "sara@example.com")).status_code == 200
    assert (await client.get(ME_URL)).json()["email"] == "sara@example.com"

    # An administrator's own account cannot be banned.
    await _login(client, "admin@example.com")
    admin_id = (await client.get(ME_URL)).json()["id"]
    self_ban = await client.post(
        f"{USERS_URL}/{admin_id}/ban", json={"value": True}
    )
    assert self_ban.status_code == 400
    assert self_ban.json()["error"]["code"] == "CANNOT_TARGET_SELF"


async def test_password_reset_returns_a_working_temporary_password(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "sara@example.com")
    await _admin_client(client, db_session_factory)

    user = (await client.get(f"{USERS_URL}?search=sara")).json()["items"][0]
    reset = await client.post(f"{USERS_URL}/{user['id']}/reset-password")

    assert reset.status_code == 200, reset.text
    temporary_password = reset.json()["temporary_password"]
    assert len(temporary_password) >= 10
    assert temporary_password != PASSWORD

    assert (await _login(client, "sara@example.com", PASSWORD)).status_code == 401
    assert (
        await _login(client, "sara@example.com", temporary_password)
    ).status_code == 200


async def test_templates_and_categories_are_managed_and_audited(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _admin_client(client, db_session_factory)

    category = await client.post(
        CATEGORIES_URL,
        json={"name": "ورزشی", "description": "تمرین و تناسب اندام", "color": "#7c3aed"},
    )
    assert category.status_code == 201, category.text
    assert category.json()["name"] == "ورزشی"

    duplicate = await client.post(CATEGORIES_URL, json={"name": "ورزشی"})
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "CATEGORY_ALREADY_EXISTS"

    template = await client.post(
        TEMPLATES_URL,
        json={
            "title": "برنامه ورزشی ۳۰ روزه",
            "description": "تمرین‌های خانگی روزانه",
            "category": "ورزشی",
            "duration_days": 30,
            "is_published": True,
        },
    )
    assert template.status_code == 201, template.text
    template_id = template.json()["id"]
    assert template.json()["title"] == "برنامه ورزشی ۳۰ روزه"

    blank_title = await client.post(TEMPLATES_URL, json={"title": "   "})
    assert blank_title.status_code == 422

    updated = await client.put(
        f"{TEMPLATES_URL}/{template_id}",
        json={"title": "برنامه ورزشی ۲۱ روزه", "duration_days": 21},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "برنامه ورزشی ۲۱ روزه"
    assert updated.json()["duration_days"] == 21
    # Untouched fields survive a partial update.
    assert updated.json()["category"] == "ورزشی"

    listed = await client.get(TEMPLATES_URL)
    assert listed.json()["total"] == 1
    assert (await client.get(CATEGORIES_URL)).json()["total"] == 1

    deleted = await client.delete(f"{TEMPLATES_URL}/{template_id}")
    assert deleted.status_code == 204
    assert (await client.get(TEMPLATES_URL)).json()["total"] == 0

    audit = await client.get(f"{LOGS_URL}?level=audit")
    events = {item["event"] for item in audit.json()["items"]}
    assert {"category.created", "template.created", "template.updated", "template.deleted"} <= events


async def test_broadcast_is_recorded_and_listed(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "sara@example.com")
    await _admin_client(client, db_session_factory)

    sent = await client.post(
        BROADCASTS_URL,
        json={"title": "به‌روزرسانی", "body": "اپلیکیشن فردا به‌روزرسانی می‌شود."},
    )
    assert sent.status_code == 201, sent.text
    assert sent.json()["recipients"] == 2
    assert sent.json()["audience"] == "all"

    blank_body = await client.post(
        BROADCASTS_URL, json={"title": "عنوان", "body": "  "}
    )
    assert blank_body.status_code == 422

    listed = await client.get(BROADCASTS_URL)
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["title"] == "به‌روزرسانی"

    broadcast_id = sent.json()["id"]
    assert (await client.delete(f"{BROADCASTS_URL}/{broadcast_id}")).status_code == 204
    assert (await client.get(BROADCASTS_URL)).json()["total"] == 0
