"""Authentication routes. HTTP concerns only; rules live in the services."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.schemas.auth import RegisterRequest, UserResponse
from app.services.identity import register_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def register(payload: RegisterRequest, session: SessionDep) -> UserResponse:
    """Create an account and return its public profile."""
    user = await register_user(session, email=payload.email, password=payload.password)
    return UserResponse.model_validate(user)
