"""Identity application services: registration, authentication, and token issuing."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.infrastructure.db.models import RefreshToken, User

# A valid Argon2id hash of a throwaway value. Verifying against it when no user
# matches keeps response time similar to a wrong-password attempt, so callers
# cannot infer whether an email exists.
_DUMMY_PASSWORD_HASH = hash_password("timing-equalizer-not-a-real-account")


class EmailAlreadyExistsError(AppError):
    """Raised when registration targets an email that is already taken."""

    status_code = 400
    code = "EMAIL_ALREADY_EXISTS"
    message = "Email is already registered."


class InvalidCredentialsError(AppError):
    """Raised for both unknown emails and wrong passwords, without distinguishing them."""

    status_code = 401
    code = "INVALID_CREDENTIALS"
    message = "Invalid email or password"


class InvalidRefreshTokenError(AppError):
    """Raised when a refresh token is unknown, expired, or replayed."""

    status_code = 401
    code = "INVALID_REFRESH_TOKEN"
    message = "Refresh token is invalid or expired."


async def register_user(session: AsyncSession, *, email: str, password: str) -> User:
    """Create a user with a unique, lowercased email and an Argon2id hash."""
    existing = await session.scalar(select(User.id).where(User.email == email))
    if existing is not None:
        raise EmailAlreadyExistsError

    user = User(email=email, password_hash=hash_password(password))
    session.add(user)

    try:
        await session.commit()
    except IntegrityError as exc:
        # Lost a race against a concurrent registration for the same email.
        await session.rollback()
        raise EmailAlreadyExistsError from exc

    await session.refresh(user)
    return user


async def authenticate_user(
    session: AsyncSession, *, email: str, password: str
) -> User | None:
    """Return the matching user, or None for an unknown email or wrong password."""
    user = await session.scalar(select(User).where(User.email == email))
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH

    if not verify_password(password, password_hash):
        return None

    return user


async def issue_tokens(session: AsyncSession, user: User) -> tuple[str, str]:
    """Create an access token and the first refresh token of a new login family."""
    settings = get_settings()

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = generate_refresh_token()

    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            family_id=str(uuid.uuid4()),
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.refresh_token_ttl_days),
        )
    )
    await session.commit()

    return access_token, refresh_token


async def _revoke_family(
    session: AsyncSession, family_id: str, revoked_at: datetime
) -> None:
    """Revoke every still-active token in a login family."""
    await session.execute(
        update(RefreshToken)
        .where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=revoked_at)
        .execution_options(synchronize_session=False)
    )
    await session.commit()


async def rotate_refresh_token(
    session: AsyncSession, presented_token: str
) -> tuple[str, str]:
    """Rotate a refresh token, revoking the whole family if a used token is replayed.

    The row is selected ``FOR UPDATE`` so two concurrent refreshes with the same
    token serialize on PostgreSQL: the loser sees ``revoked_at`` set and takes the
    replay path instead of minting a second valid token. SQLite serializes writes
    and ignores ``FOR UPDATE``.
    """
    settings = get_settings()
    now = datetime.now(UTC)

    row = await session.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_refresh_token(presented_token))
        .with_for_update()
    )

    if row is None:
        raise InvalidRefreshTokenError

    if row.revoked_at is not None:
        # Replay: a token from this family was presented after it was rotated.
        # Assume the chain is compromised and force a fresh login.
        await _revoke_family(session, row.family_id, now)
        raise InvalidRefreshTokenError

    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        # SQLite drops timezone information on round-trip (stored as naive UTC).
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        raise InvalidRefreshTokenError

    user = await session.get(User, row.user_id)
    if user is None:
        raise InvalidRefreshTokenError

    row.revoked_at = now

    new_refresh_token = generate_refresh_token()
    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh_token),
            family_id=row.family_id,
            expires_at=now + timedelta(days=settings.refresh_token_ttl_days),
        )
    )

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    await session.commit()

    return access_token, new_refresh_token


async def revoke_refresh_token(session: AsyncSession, token: str) -> None:
    """Revoke every active token in the login family that ``token`` belongs to.

    Logout therefore ends that session across all its rotated tokens, while other
    devices (separate families) stay signed in.
    """
    row = await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(token))
    )
    if row is None:
        return

    await _revoke_family(session, row.family_id, datetime.now(UTC))


async def update_timezone(session: AsyncSession, user: User, timezone: str) -> None:
    """Persist an already-validated IANA timezone for the user.

    Existing check-ins keep the local dates and timezones recorded at the time
    (AGENTS.md section 7); only later interpretations use the new value.
    """
    user.timezone = timezone
    await session.commit()
