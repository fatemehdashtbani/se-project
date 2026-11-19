"""Identity application services: registration, authentication, and token issuing."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
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
    """Create an access token and a tracked refresh token for the user."""
    settings = get_settings()

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = generate_refresh_token()

    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.refresh_token_ttl_days),
        )
    )
    await session.commit()

    return access_token, refresh_token


async def revoke_refresh_token(session: AsyncSession, token: str) -> None:
    """Revoke the refresh token matching the presented value, if it is still active."""
    revoked = await session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(token),
            RefreshToken.revoked_at.is_(None),
        )
    )
    if revoked is None:
        return

    revoked.revoked_at = datetime.now(UTC)
    await session.commit()
