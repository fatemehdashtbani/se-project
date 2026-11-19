"""Shared FastAPI dependencies."""

import uuid
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import decode_access_token
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session


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

    return user
