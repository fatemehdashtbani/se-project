"""Shared FastAPI dependencies."""

import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated, Literal

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import decode_access_token
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.infrastructure.email import EmailSender, SmtpEmailSender

Role = Literal["user", "mentor", "admin"]


async def get_current_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Resolve the authenticated user from the access-token cookie.

    The cookie is the only accepted transport (SPEC FR-F019-006). A missing
    cookie yields UNAUTHORIZED, while a present-but-bad token surfaces the
    decoded error (TOKEN_EXPIRED or INVALID_TOKEN) so clients can refresh.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise AppError("Authentication required", code="UNAUTHORIZED", status_code=401)

    claims = decode_access_token(token)

    try:
        user_id = uuid.UUID(str(claims.get("sub")))
    except ValueError as exc:
        raise AppError(
            "Access token is invalid",
            code="INVALID_TOKEN",
            status_code=401,
        ) from exc

    user = await session.get(User, user_id)
    if user is None:
        raise AppError("Authentication required", code="UNAUTHORIZED", status_code=401)

    # A ban or a deactivation takes effect on the very next request, without
    # waiting for the short-lived access token to expire (F-037).
    if user.is_banned or not user.is_active:
        raise AppError(
            "This account is disabled. Contact the platform administrator.",
            code="ACCOUNT_DISABLED",
            status_code=403,
        )

    return user


def get_email_sender() -> EmailSender:
    """Return the configured email transport; tests override this dependency."""
    return SmtpEmailSender(get_settings())


def require_role(required_role: Role) -> Callable[..., Awaitable[User]]:
    """Build a dependency that admits only users holding ``required_role``.

    The role is read from the database by ``get_current_user``, never from the
    token claims, so a role change takes effect on the very next request
    (ADR-0006). The parameter is a ``Literal`` so a misspelled role fails at
    import time instead of silently denying every caller.
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role != required_role:
            raise AppError(
                "Insufficient permissions",
                code="FORBIDDEN",
                status_code=403,
            )

        return current_user

    return role_checker
