"""Authentication routes. HTTP concerns only; rules live in the services."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.auth import LoginRequest, MeResponse, RegisterRequest, UserResponse
from app.services.identity import (
    InvalidCredentialsError,
    authenticate_user,
    issue_tokens,
    register_user,
    revoke_refresh_token,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


def _session_cookie(
    response: JSONResponse, name: str, value: str, max_age: int
) -> None:
    """Set a session cookie with the attributes mandated by SPEC section 9."""
    settings = get_settings()
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def register(payload: RegisterRequest, session: SessionDep) -> UserResponse:
    """Create an account and return its public profile."""
    user = await register_user(session, email=payload.email, password=payload.password)
    return UserResponse.model_validate(user)


@router.post("/login")
async def login(payload: LoginRequest, session: SessionDep) -> JSONResponse:
    """Authenticate the user and return HttpOnly session cookies."""
    user = await authenticate_user(
        session, email=payload.email, password=payload.password
    )
    if user is None:
        raise InvalidCredentialsError

    access_token, refresh_token = await issue_tokens(session, user)
    settings = get_settings()

    response = JSONResponse({"message": "Logged in successfully"})
    _session_cookie(
        response, "access_token", access_token, settings.access_token_ttl_minutes * 60
    )
    _session_cookie(
        response,
        "refresh_token",
        refresh_token,
        settings.refresh_token_ttl_days * 24 * 60 * 60,
    )
    return response


@router.get("/me", response_model=MeResponse)
async def me(current_user: CurrentUserDep) -> MeResponse:
    """Return the authenticated user's own profile."""
    return MeResponse.model_validate(current_user)


@router.post("/logout")
async def logout(request: Request, session: SessionDep) -> JSONResponse:
    """Revoke the presented refresh token and clear both session cookies.

    Logging out is idempotent: it succeeds even when no refresh cookie exists.
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await revoke_refresh_token(session, refresh_token)

    response = JSONResponse({"message": "Logged out successfully"})
    _session_cookie(response, "access_token", "", 0)
    _session_cookie(response, "refresh_token", "", 0)
    return response
