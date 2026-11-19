"""Identity application services: registration and, later, login and refresh."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password
from app.infrastructure.db.models import User


class EmailAlreadyExistsError(AppError):
    """Raised when registration targets an email that is already taken."""

    status_code = 400
    code = "EMAIL_ALREADY_EXISTS"
    message = "Email is already registered."


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
