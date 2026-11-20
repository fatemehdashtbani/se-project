"""Integration tests for the role-based access-control dependency (F-003).

The protected route is declared here instead of in the application so that the
test-only endpoint never reaches production (SPEC section 4).
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.dependencies import require_role
from app.infrastructure.db.models import User
from app.main import app

ADMIN_URL = "/api/v1/admin/test"
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

PASSWORD = "secret123"

router = APIRouter()


@router.get("/admin/test")
async def admin_only(
    user: Annotated[User, Depends(require_role("admin"))],
) -> dict[str, str]:
    return {"message": f"admin only: {user.email}"}


app.include_router(router, prefix="/api/v1")


async def _register(client: AsyncClient, email: str) -> None:
    response = await client.post(
        REGISTER_URL, json={"email": email, "password": PASSWORD}
    )
    assert response.status_code == 201, response.text


async def _set_role(
    db_session_factory: async_sessionmaker[AsyncSession], email: str, role: str
) -> None:
    """Promote a registered user directly in the database, as seeding would."""
    async with db_session_factory() as session:
        await session.execute(update(User).where(User.email == email).values(role=role))
        await session.commit()


async def _login(client: AsyncClient, email: str) -> None:
    response = await client.post(LOGIN_URL, json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text


async def test_admin_route_rejects_unauthenticated_requests(
    client: AsyncClient,
) -> None:
    response = await client.get(ADMIN_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_admin_route_forbids_regular_users(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "regular@example.com")
    await _login(client, "regular@example.com")

    response = await client.get(ADMIN_URL)

    assert response.status_code == 403
    body = response.json()
    assert body["error"]["code"] == "FORBIDDEN"
    assert body["error"]["message"] == "Insufficient permissions"


async def test_admin_route_allows_admins(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await _register(client, "admin@example.com")
    await _set_role(db_session_factory, "admin@example.com", "admin")
    await _login(client, "admin@example.com")

    response = await client.get(ADMIN_URL)

    assert response.status_code == 200
    assert response.json() == {"message": "admin only: admin@example.com"}


async def test_promotion_applies_to_a_token_minted_before_the_change(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """ADR-0006: role changes take effect immediately, not at token expiry.

    The token's ``role`` claim still says ``user``; the check must read the
    database. A JWT-claim implementation would answer 403 here.
    """
    await _register(client, "late-admin@example.com")
    await _login(client, "late-admin@example.com")

    await _set_role(db_session_factory, "late-admin@example.com", "admin")

    response = await client.get(ADMIN_URL)

    assert response.status_code == 200


async def test_demotion_applies_to_a_token_minted_before_the_change(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """ADR-0006: a stale ``admin`` claim must not keep access after demotion."""
    await _register(client, "demoted@example.com")
    await _set_role(db_session_factory, "demoted@example.com", "admin")
    await _login(client, "demoted@example.com")

    await _set_role(db_session_factory, "demoted@example.com", "user")

    response = await client.get(ADMIN_URL)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
