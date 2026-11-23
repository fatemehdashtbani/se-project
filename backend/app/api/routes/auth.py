"""Authentication routes. HTTP concerns only; rules live in the services."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    RegisterRequest,
    TimezoneUpdateRequest,
    UserResponse,
)
from app.services.identity import (
    InvalidCredentialsError,
    authenticate_user,
    issue_tokens,
    register_user,
    revoke_refresh_token,
    rotate_refresh_token,
    update_timezone,
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


def _token_response(
    message: str, access_token: str, refresh_token: str
) -> JSONResponse:
    """Return ``message`` with both session cookies attached."""
    settings = get_settings()
    response = JSONResponse({"message": message})
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


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def register(payload: RegisterRequest, session: SessionDep) -> UserResponse:
    """Create an account and return its public profile."""
    user = await register_user(
        session,
        email=payload.email,
        password=payload.password,
        username=payload.username,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone_number=payload.phone_number,
    )
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
    return _token_response("Logged in successfully", access_token, refresh_token)


@router.post("/refresh")
async def refresh(request: Request, session: SessionDep) -> JSONResponse:
    """Rotate the session: new access token and a new refresh token in the family."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise AppError(
            "Refresh token is required", code="UNAUTHORIZED", status_code=401
        )

    access_token, new_refresh_token = await rotate_refresh_token(session, refresh_token)
    return _token_response(
        "Tokens refreshed successfully", access_token, new_refresh_token
    )


@router.get("/me", response_model=MeResponse)
async def me(current_user: CurrentUserDep) -> MeResponse:
    """Return the authenticated user's own profile."""
    return MeResponse.model_validate(current_user)


@router.put("/me/timezone")
async def update_my_timezone(
    payload: TimezoneUpdateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict[str, str]:
    """Update the signed-in user's IANA timezone (SPEC FR-F019-007)."""
    await update_timezone(session, current_user, payload.timezone)
    return {"message": "Timezone updated successfully", "timezone": payload.timezone}


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
