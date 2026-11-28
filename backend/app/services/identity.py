"""Identity application services: registration, authentication, and token issuing."""

import re
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select, update
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
from app.schemas.auth import ProfileUpdateRequest

# A valid Argon2id hash of a throwaway value. Verifying against it when no user
# matches keeps response time similar to a wrong-password attempt, so callers
# cannot infer whether an email exists.
_DUMMY_PASSWORD_HASH = hash_password("timing-equalizer-not-a-real-account")


def normalize_login_identifier(value: str) -> str:
    """Normalize an email or phone number the way registration stores it.

    Emails are lowercased; phone numbers lose the spaces and dashes people
    type. Registration applies the same rules, so what is stored is what is
    compared here.
    """
    identifier = value.strip()
    if "@" in identifier:
        return identifier.lower()
    return re.sub(r"[\s-]", "", identifier)


class EmailAlreadyExistsError(AppError):
    """Raised when registration targets an email that is already taken."""

    status_code = 400
    code = "EMAIL_ALREADY_EXISTS"
    message = "Email is already registered."


class UsernameAlreadyExistsError(AppError):
    """Raised when registration targets a username that is already taken."""

    status_code = 400
    code = "USERNAME_ALREADY_EXISTS"
    message = "Username is already taken."


class InvalidCredentialsError(AppError):
    """Raised for both unknown emails and wrong passwords, without distinguishing them."""

    status_code = 401
    code = "INVALID_CREDENTIALS"
    message = "Invalid email or password"


class UserNotFoundError(AppError):
    """Raised when an operation targets an email that has no account."""

    status_code = 404
    code = "USER_NOT_FOUND"
    message = "User not found."


class InvalidCurrentPasswordError(AppError):
    """Raised when a password change presents the wrong current password."""

    status_code = 400
    code = "INVALID_CURRENT_PASSWORD"
    message = "Current password is incorrect."


class AccountDisabledError(AppError):
    """Raised when a banned or disabled account tries to authenticate (F-037)."""

    status_code = 403
    code = "ACCOUNT_DISABLED"
    message = "This account is disabled. Contact the platform administrator."


class InvalidRefreshTokenError(AppError):
    """Raised when a refresh token is unknown, expired, or replayed."""

    status_code = 401
    code = "INVALID_REFRESH_TOKEN"
    message = "Refresh token is invalid or expired."


async def register_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    username: str,
    first_name: str,
    last_name: str,
    phone_number: str,
) -> User:
    """Create a user with a unique email and username plus an Argon2id hash."""
    existing = await session.scalar(select(User.id).where(User.email == email))
    if existing is not None:
        raise EmailAlreadyExistsError

    taken_username = await session.scalar(
        select(User.id).where(User.username == username)
    )
    if taken_username is not None:
        raise UsernameAlreadyExistsError

    user = User(
        email=email,
        password_hash=hash_password(password),
        username=username,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
    )
    session.add(user)

    try:
        await session.commit()
    except IntegrityError as exc:
        # Lost a race against a concurrent registration for the same email or
        # username. The constraint name is dialect-specific, so ask the database
        # which value collided instead of parsing the driver message.
        await session.rollback()
        raced_username = await session.scalar(
            select(User.id).where(User.username == username)
        )
        if raced_username is not None:
            raise UsernameAlreadyExistsError from exc
        raise EmailAlreadyExistsError from exc

    await session.refresh(user)
    return user


async def promote_to_admin(session: AsyncSession, *, email: str) -> bool:
    """Grant the admin role to an existing user, idempotently.

    Returns True when the role changed. Admins are never created here: an
    operator promotes an account that already exists (ADR-0006).
    """
    user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        raise UserNotFoundError

    if user.role == "admin":
        return False

    user.role = "admin"
    await session.commit()
    return True


async def authenticate_user(
    session: AsyncSession, *, identifier: str, password: str
) -> User | None:
    """Return the account matching an email or phone identifier, or None.

    The identifier is normalized the same way registration stores it, so a
    phone typed with spaces still matches and emails stay case-insensitive.

    Only an unambiguous match is accepted. ``phone_number`` is not unique in
    the database, so a number shared by two accounts must not silently sign one
    of them in; those users can still log in with their email.
    """
    normalized = normalize_login_identifier(identifier)
    users = list(
        (
            await session.scalars(
                select(User).where(
                    or_(User.email == normalized, User.phone_number == normalized)
                )
            )
        ).all()
    )

    user = users[0] if len(users) == 1 else None
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH

    if not verify_password(password, password_hash):
        return None

    # The password is checked first so a disabled account cannot be discovered
    # without valid credentials.
    if user is not None and (user.is_banned or not user.is_active):
        raise AccountDisabledError

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
    if user.is_banned or not user.is_active:
        raise AccountDisabledError

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


async def update_profile(
    session: AsyncSession, user: User, payload: ProfileUpdateRequest
) -> User:
    """Apply only the profile fields the caller actually sent (F-031)."""
    fields = payload.model_fields_set

    if "first_name" in fields and payload.first_name is not None:
        user.first_name = payload.first_name
    if "last_name" in fields and payload.last_name is not None:
        user.last_name = payload.last_name
    if "phone_number" in fields and payload.phone_number is not None:
        user.phone_number = payload.phone_number

    await session.commit()
    await session.refresh(user)
    return user


async def _revoke_other_sessions(
    session: AsyncSession, user: User, current_refresh_token: str | None
) -> None:
    """Revoke every login family of ``user`` except the caller's own.

    A password change must end sessions an attacker may be holding. The caller's
    family is identified by the refresh cookie of this very request, so the tab
    that changed the password is not signed out.
    """
    current_family: str | None = None
    if current_refresh_token:
        current_family = await session.scalar(
            select(RefreshToken.family_id).where(
                RefreshToken.token_hash == hash_refresh_token(current_refresh_token)
            )
        )

    others = update(RefreshToken).where(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked_at.is_(None),
    )
    if current_family is not None:
        others = others.where(RefreshToken.family_id != current_family)

    await session.execute(
        others.values(revoked_at=datetime.now(UTC)).execution_options(
            synchronize_session=False
        )
    )


async def change_password(
    session: AsyncSession,
    user: User,
    *,
    current_password: str,
    new_password: str,
    current_refresh_token: str | None,
) -> None:
    """Replace the password hash after verifying the current password (F-031)."""
    if not verify_password(current_password, user.password_hash):
        raise InvalidCurrentPasswordError

    user.password_hash = hash_password(new_password)
    await _revoke_other_sessions(session, user, current_refresh_token)
    await session.commit()


async def update_timezone(session: AsyncSession, user: User, timezone: str) -> None:
    """Persist an already-validated IANA timezone for the user.

    Existing check-ins keep the local dates and timezones recorded at the time
    (AGENTS.md section 7); only later interpretations use the new value.
    """
    user.timezone = timezone
    await session.commit()
