"""Password-reset use cases (F-022).

The request endpoint never reveals whether an address is registered; the token
itself is random, stored only as a SHA-256 hash, expires, and can be used once.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import hash_password
from app.infrastructure.db.models import PasswordResetToken, RefreshToken, User


class InvalidResetTokenError(AppError):
    """Raised when a reset token is unknown, expired, or already used."""

    status_code = 400
    code = "INVALID_RESET_TOKEN"
    message = "This password reset link is invalid or has expired."


def hash_reset_token(token: str) -> str:
    """Hash a reset token for storage; the raw value never touches the database."""
    return hashlib.sha256(token.encode()).hexdigest()


def _as_utc(value: datetime) -> datetime:
    """Treat a naive datetime as UTC (SQLite drops the timezone on round-trip)."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def build_reset_url(token: str) -> str:
    """Build the frontend link that carries the raw token."""
    base = get_settings().frontend_base_url.rstrip("/")
    return f"{base}/reset-password?token={token}"


async def request_password_reset(
    session: AsyncSession, *, email: str
) -> tuple[str, str] | None:
    """Create a reset token for a registered address.

    Returns ``(email, raw_token)`` when a message should be sent, or None when
    the address is unknown or the per-account cooldown is still running. Both
    cases look identical to the caller, so the endpoint cannot be used to
    discover registered emails.
    """
    settings = get_settings()
    now = datetime.now(UTC)

    user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        return None

    last_sent_at = await session.scalar(
        select(PasswordResetToken.created_at)
        .where(PasswordResetToken.user_id == user.id)
        .order_by(PasswordResetToken.created_at.desc())
        .limit(1)
    )
    if last_sent_at is not None and now - _as_utc(last_sent_at) < timedelta(
        seconds=settings.password_reset_resend_seconds
    ):
        return None

    raw_token = secrets.token_urlsafe(32)
    session.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hash_reset_token(raw_token),
            expires_at=now + timedelta(minutes=settings.password_reset_ttl_minutes),
        )
    )
    await session.commit()

    return user.email, raw_token


async def discard_password_reset(session: AsyncSession, *, token: str) -> None:
    """Remove a token whose email could not be delivered, so it is not left valid."""
    row = await session.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_reset_token(token)
        )
    )
    if row is None:
        return

    await session.delete(row)
    await session.commit()


async def reset_password(
    session: AsyncSession, *, token: str, new_password: str
) -> None:
    """Set a new password from a valid token, then end every existing session.

    A row is selected ``FOR UPDATE`` so two concurrent submissions of the same
    link serialize on PostgreSQL and only the first one succeeds. All other
    outstanding reset links for the account are invalidated as well.
    """
    now = datetime.now(UTC)

    row = await session.scalar(
        select(PasswordResetToken)
        .where(PasswordResetToken.token_hash == hash_reset_token(token))
        .with_for_update()
    )

    if (
        row is None
        or row.used_at is not None
        or _as_utc(row.expires_at) <= now
    ):
        raise InvalidResetTokenError

    user = await session.get(User, row.user_id)
    if user is None:
        raise InvalidResetTokenError

    user.password_hash = hash_password(new_password)
    row.used_at = now

    await session.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=now)
        .execution_options(synchronize_session=False)
    )
    await session.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
        .execution_options(synchronize_session=False)
    )
    await session.commit()
