"""Integration tests for the registration and login endpoints.

These tests describe the contract from F-019 FR-F019-001, FR-F019-002 and SPEC section 3.
"""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from helpers import registration_payload
from httpx import AsyncClient, Response
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.infrastructure.db.models import RefreshToken, User

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
ME_URL = "/api/v1/auth/me"
TIMEZONE_URL = "/api/v1/auth/me/timezone"
LOGOUT_URL = "/api/v1/auth/logout"

PASSWORD = "secret123"


async def _register_user(
    client: AsyncClient, email: str, password: str = PASSWORD
) -> Response:
    return await client.post(
        REGISTER_URL, json=registration_payload(email, password=password)
    )


async def _login(client: AsyncClient, email: str, password: str = PASSWORD) -> Response:
    return await client.post(
        LOGIN_URL, json={"identifier": email, "password": password}
    )


def _set_cookie_headers(response: Response) -> dict[str, str]:
    """Map cookie name to its raw ``Set-Cookie`` header."""
    headers: dict[str, str] = {}
    for raw in response.headers.get_list("set-cookie"):
        name = raw.split("=", 1)[0].strip()
        headers[name] = raw
    return headers


def _cookie_payload(header: str) -> str:
    """Return the (unquoted) value portion of a raw ``Set-Cookie`` header."""
    pair = header.split(";", 1)[0]
    _, _, value = pair.partition("=")
    return value.strip().strip('"')


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def _refresh_rows(
    db_session_factory: async_sessionmaker[AsyncSession],
    email: str,
) -> dict[str, RefreshToken]:
    """Return this user's refresh-token rows keyed by token hash."""
    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
        rows = (
            (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.user_id == user.id)
                )
            )
            .scalars()
            .all()
        )

    return {row.token_hash: row for row in rows}


async def test_register_creates_user_with_hashed_password(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    response = await client.post(
        REGISTER_URL,
        json=registration_payload("New.User@Example.com", password="secret123"),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new.user@example.com"
    assert body["role"] == "user"
    assert body["timezone"] == "UTC"
    assert "password" not in body
    assert "password_hash" not in body

    async with db_session_factory() as session:
        user = (
            await session.execute(
                select(User).where(User.email == "new.user@example.com")
            )
        ).scalar_one()

    assert user.password_hash != "secret123"
    assert user.password_hash.startswith("$argon2id$")


async def test_register_rejects_duplicate_email(client: AsyncClient) -> None:
    payload = registration_payload("duplicate@example.com")

    first = await client.post(REGISTER_URL, json=payload)
    assert first.status_code == 201

    second = await client.post(REGISTER_URL, json=payload)

    assert second.status_code == 400
    assert second.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


async def test_register_rejects_short_password(client: AsyncClient) -> None:
    response = await client.post(
        REGISTER_URL,
        json=registration_payload("short@example.com", password="short"),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_register_rejects_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        REGISTER_URL,
        json=registration_payload("notanemail"),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_login_returns_http_only_cookies_and_records_refresh_token(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "login.user@example.com"
    assert (await _register_user(client, email)).status_code == 201

    response = await client.post(
        LOGIN_URL, json={"identifier": email, "password": PASSWORD}
    )

    assert response.status_code == 200

    cookie_headers = _set_cookie_headers(response)
    assert "access_token" in cookie_headers
    assert "refresh_token" in cookie_headers
    assert "httponly" in cookie_headers["access_token"].lower()
    assert "httponly" in cookie_headers["refresh_token"].lower()

    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
        tokens = (
            (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.user_id == user.id)
                )
            )
            .scalars()
            .all()
        )

    assert len(tokens) == 1
    refresh_row = tokens[0]
    assert refresh_row.revoked_at is None

    expires_at = refresh_row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    assert expires_at > datetime.now(UTC)

    refresh_cookie = response.cookies["refresh_token"]
    assert refresh_row.token_hash == hashlib.sha256(refresh_cookie.encode()).hexdigest()
    assert len(refresh_row.token_hash) == 64


async def test_login_sets_browser_session_cookies_without_remember_me(
    client: AsyncClient,
) -> None:
    """Unchecked "remember me": the browser drops the cookies when it closes.

    No ``remember_session`` marker is left behind, so a later refresh cannot
    accidentally promote the session to a persistent one.
    """
    email = "session.only@example.com"
    assert (await _register_user(client, email)).status_code == 201

    response = await _login(client, email)

    assert response.status_code == 200
    cookie_headers = _set_cookie_headers(response)
    for name in ("access_token", "refresh_token"):
        assert "max-age" not in cookie_headers[name].lower()

    assert _cookie_payload(cookie_headers["remember_session"]) == ""
    assert "max-age=0" in cookie_headers["remember_session"].lower()


async def test_login_sets_persistent_cookies_with_remember_me(
    client: AsyncClient,
) -> None:
    """Checked "remember me": Max-Age keeps the session across browser restarts."""
    email = "remember.me@example.com"
    assert (await _register_user(client, email)).status_code == 201

    response = await client.post(
        LOGIN_URL,
        json={"identifier": email, "password": PASSWORD, "remember_me": True},
    )

    assert response.status_code == 200
    cookie_headers = _set_cookie_headers(response)
    settings = get_settings()
    access_max_age = settings.access_token_ttl_minutes * 60
    refresh_max_age = settings.refresh_token_ttl_days * 24 * 60 * 60

    assert f"max-age={access_max_age}" in cookie_headers["access_token"].lower()
    assert f"max-age={refresh_max_age}" in cookie_headers["refresh_token"].lower()
    assert f"max-age={refresh_max_age}" in cookie_headers["remember_session"].lower()
    assert _cookie_payload(cookie_headers["remember_session"]) == "1"


async def test_refresh_keeps_the_remember_me_lifetime(client: AsyncClient) -> None:
    """Rotation must not turn a remembered session into a browser-session one."""
    email = "remember.refresh@example.com"
    assert (await _register_user(client, email)).status_code == 201
    login = await client.post(
        LOGIN_URL,
        json={"identifier": email, "password": PASSWORD, "remember_me": True},
    )
    assert login.status_code == 200

    response = await client.post(REFRESH_URL)

    assert response.status_code == 200
    cookie_headers = _set_cookie_headers(response)
    for name in ("access_token", "refresh_token", "remember_session"):
        assert "max-age" in cookie_headers[name].lower()


async def test_refresh_of_a_browser_session_stays_session_only(
    client: AsyncClient,
) -> None:
    """Rotation without the marker must not extend the session past the browser."""
    email = "session.refresh@example.com"
    assert (await _register_user(client, email)).status_code == 201
    assert (await _login(client, email)).status_code == 200

    response = await client.post(REFRESH_URL)

    assert response.status_code == 200
    cookie_headers = _set_cookie_headers(response)
    for name in ("access_token", "refresh_token"):
        assert "max-age" not in cookie_headers[name].lower()
    assert "max-age=0" in cookie_headers["remember_session"].lower()


async def test_login_rejects_wrong_password(client: AsyncClient) -> None:
    email = "wrong.password@example.com"
    assert (await _register_user(client, email)).status_code == 201

    response = await client.post(
        LOGIN_URL,
        json={"identifier": email, "password": "different-secret"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_login_rejects_unknown_email_without_disclosing_it(
    client: AsyncClient,
) -> None:
    response = await client.post(
        LOGIN_URL,
        json={"identifier": "nobody@example.com", "password": PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_login_accepts_the_phone_number_as_identifier(
    client: AsyncClient,
) -> None:
    email = "phone.login@example.com"
    payload = registration_payload(email, phone_number="09121234567")
    assert (await client.post(REGISTER_URL, json=payload)).status_code == 201

    response = await client.post(
        LOGIN_URL, json={"identifier": "09121234567", "password": PASSWORD}
    )

    assert response.status_code == 200
    me = await client.get(ME_URL)
    assert me.status_code == 200
    assert me.json()["email"] == email


async def test_login_normalizes_a_typed_phone_number(client: AsyncClient) -> None:
    """Registration stores ``09123456789``, so spaced login input must match it."""
    email = "phone.spaces@example.com"
    payload = registration_payload(email, phone_number="09123456789")
    assert (await client.post(REGISTER_URL, json=payload)).status_code == 201

    response = await client.post(
        LOGIN_URL, json={"identifier": "0912 345 6789", "password": PASSWORD}
    )

    assert response.status_code == 200


async def test_login_matches_the_email_case_insensitively(
    client: AsyncClient,
) -> None:
    email = "case.login@example.com"
    assert (await _register_user(client, email)).status_code == 201

    response = await client.post(
        LOGIN_URL, json={"identifier": "CASE.Login@Example.COM", "password": PASSWORD}
    )

    assert response.status_code == 200


async def test_login_requires_an_identifier(client: AsyncClient) -> None:
    response = await client.post(LOGIN_URL, json={"password": PASSWORD})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_login_rejects_a_phone_number_shared_by_two_accounts(
    client: AsyncClient,
) -> None:
    """A mobile identifier is only safe when it resolves to exactly one account."""
    first = registration_payload("shared.one@example.com", phone_number="09120001111")
    second = registration_payload("shared.two@example.com", phone_number="09120001111")
    assert (await client.post(REGISTER_URL, json=first)).status_code == 201
    assert (await client.post(REGISTER_URL, json=second)).status_code == 201

    response = await client.post(
        LOGIN_URL, json={"identifier": "09120001111", "password": PASSWORD}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_me_returns_current_user(client: AsyncClient) -> None:
    email = "me.valid@example.com"
    registration = await _register_user(client, email)
    user_id = registration.json()["id"]

    assert (await _login(client, email)).status_code == 200

    response = await client.get(ME_URL)

    assert response.status_code == 200
    profile = registration_payload(email)
    assert response.json() == {
        "id": user_id,
        "email": email,
        "role": "user",
        "timezone": "UTC",
        "username": profile["username"],
        "first_name": profile["first_name"],
        "last_name": profile["last_name"],
        "phone_number": profile["phone_number"],
    }


async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get(ME_URL)

    assert response.status_code == 401
    assert response.json()["error"]["code"] in {"UNAUTHORIZED", "NOT_AUTHENTICATED"}


async def test_me_rejects_expired_token(client: AsyncClient) -> None:
    settings = get_settings()
    expired_token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    response = await client.get(
        ME_URL,
        headers={"Cookie": f"access_token={expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "TOKEN_EXPIRED"


async def test_logout_clears_cookies_and_revokes_refresh_token(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "logout@example.com"
    assert (await _register_user(client, email)).status_code == 201
    assert (await _login(client, email)).status_code == 200

    response = await client.post(LOGOUT_URL)

    assert response.status_code in {200, 204}

    cookie_headers = _set_cookie_headers(response)
    for name in ("access_token", "refresh_token", "remember_session"):
        assert name in cookie_headers
        assert _cookie_payload(cookie_headers[name]) == ""
        assert "max-age=0" in cookie_headers[name].lower()

    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
        tokens = (
            (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.user_id == user.id)
                )
            )
            .scalars()
            .all()
        )

    assert len(tokens) == 1
    assert tokens[0].revoked_at is not None


async def test_refresh_rotates_tokens_and_revokes_the_previous_row(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "refresh.valid@example.com"
    assert (await _register_user(client, email)).status_code == 201
    login = await _login(client, email)
    assert login.status_code == 200

    old_refresh = login.cookies["refresh_token"]
    old_hash = _hash_token(old_refresh)

    response = await client.post(REFRESH_URL)

    assert response.status_code == 200

    cookie_headers = _set_cookie_headers(response)
    assert "access_token" in cookie_headers
    assert "refresh_token" in cookie_headers

    new_refresh = _cookie_payload(cookie_headers["refresh_token"])
    new_hash = _hash_token(new_refresh)
    assert new_refresh != old_refresh

    rows = await _refresh_rows(db_session_factory, email)

    assert old_hash in rows
    assert new_hash in rows
    assert len(rows) == 2
    assert rows[old_hash].revoked_at is not None
    assert rows[new_hash].revoked_at is None


async def test_refresh_replay_revokes_the_whole_token_family(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "refresh.replay@example.com"
    assert (await _register_user(client, email)).status_code == 201
    login = await _login(client, email)
    assert login.status_code == 200

    token_one = login.cookies["refresh_token"]

    rotation = await client.post(REFRESH_URL)
    assert rotation.status_code == 200
    token_two = _cookie_payload(_set_cookie_headers(rotation)["refresh_token"])
    assert token_two != token_one

    # Replay the already-rotated token the way an attacker holding it would.
    client.cookies.clear()
    replay = await client.post(
        REFRESH_URL,
        headers={"Cookie": f"refresh_token={token_one}"},
    )

    assert replay.status_code == 401
    assert replay.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"

    rows = await _refresh_rows(db_session_factory, email)
    assert _hash_token(token_two) in rows
    assert all(row.revoked_at is not None for row in rows.values())


async def test_refresh_rejects_missing_and_garbage_tokens(client: AsyncClient) -> None:
    without_cookie = await client.post(REFRESH_URL)
    assert without_cookie.status_code == 401

    client.cookies.clear()
    garbage = await client.post(
        REFRESH_URL,
        headers={"Cookie": "refresh_token=garbage-token"},
    )

    assert garbage.status_code == 401


async def test_logout_with_an_older_rotated_token_revokes_the_active_one(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Logout is family-scoped: presenting any member ends the whole login chain.

    A single active token can only be observed this way, because rotation always
    revokes the previous row; presenting the older row proves the family (not just
    the presented row) is what gets revoked.
    """
    email = "logout.family@example.com"
    assert (await _register_user(client, email)).status_code == 201
    login = await _login(client, email)
    assert login.status_code == 200
    token_one = login.cookies["refresh_token"]

    rotation = await client.post(REFRESH_URL)
    assert rotation.status_code == 200
    token_two = _cookie_payload(_set_cookie_headers(rotation)["refresh_token"])
    assert token_two != token_one

    client.cookies.clear()
    logout = await client.post(
        LOGOUT_URL,
        headers={"Cookie": f"refresh_token={token_one}"},
    )
    assert logout.status_code == 200

    rows = await _refresh_rows(db_session_factory, email)
    assert _hash_token(token_one) in rows
    assert _hash_token(token_two) in rows
    assert rows[_hash_token(token_two)].revoked_at is not None


async def test_update_timezone_persists_and_me_reflects_it(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "timezone.update@example.com"
    assert (await _register_user(client, email)).status_code == 201
    assert (await _login(client, email)).status_code == 200

    response = await client.put(TIMEZONE_URL, json={"timezone": "Asia/Tehran"})

    assert response.status_code == 200
    assert response.json()["timezone"] == "Asia/Tehran"

    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
    assert user.timezone == "Asia/Tehran"

    me = await client.get(ME_URL)
    assert me.status_code == 200
    assert me.json()["timezone"] == "Asia/Tehran"


async def test_update_timezone_rejects_unknown_iana_zone(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    email = "timezone.invalid@example.com"
    assert (await _register_user(client, email)).status_code == 201
    assert (await _login(client, email)).status_code == 200

    response = await client.put(TIMEZONE_URL, json={"timezone": "Mars/Phobos"})

    assert response.status_code in {400, 422}
    assert response.json()["error"]["code"] in {"VALIDATION_ERROR", "INVALID_TIMEZONE"}

    async with db_session_factory() as session:
        user = (
            await session.execute(select(User).where(User.email == email))
        ).scalar_one()
    assert user.timezone == "UTC"
