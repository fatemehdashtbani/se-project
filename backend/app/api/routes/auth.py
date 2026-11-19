"""Authentication routes. HTTP concerns only; rules live in the services."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.infrastructure.db.session import get_session
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.services.identity import (
    InvalidCredentialsError,
    authenticate_user,
    issue_tokens,
    register_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


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
    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.access_token_ttl_minutes * 60,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    return response
