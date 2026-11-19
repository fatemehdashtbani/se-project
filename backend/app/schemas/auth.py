"""Request and response schemas for authentication."""

import re
import uuid
from datetime import datetime
from zoneinfo import available_timezones

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


def normalize_email(value: str) -> str:
    """Trim, lowercase, and reject malformed addresses."""
    email = value.strip().lower()
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("invalid email format")
    return email


class RegisterRequest(BaseModel):
    """Payload accepted by ``POST /api/v1/auth/register``."""

    email: str = Field(max_length=320)
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH
    )

    @field_validator("email")
    @classmethod
    def normalize(cls, value: str) -> str:
        return normalize_email(value)


class LoginRequest(BaseModel):
    """Payload accepted by ``POST /api/v1/auth/login``.

    The password is only required to be present: rejecting short passwords here
    would leak the registration policy and turn a mistyped password into a 422.
    """

    email: str = Field(max_length=320)
    password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)

    @field_validator("email")
    @classmethod
    def normalize(cls, value: str) -> str:
        return normalize_email(value)


class UserResponse(BaseModel):
    """Public representation of a user. Never carries the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    timezone: str
    created_at: datetime


class MeResponse(BaseModel):
    """Profile returned by ``GET /api/v1/auth/me`` (SPEC FR-F019-006)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    timezone: str


class TimezoneUpdateRequest(BaseModel):
    """Payload accepted by ``PUT /api/v1/auth/me/timezone`` (SPEC FR-F019-007)."""

    timezone: str = Field(min_length=1, max_length=64)

    @field_validator("timezone")
    @classmethod
    def validate_iana_zone(cls, value: str) -> str:
        """Accept only keys present in the standard IANA timezone database."""
        zone = value.strip()
        if zone not in available_timezones():
            raise ValueError("Invalid IANA timezone")
        return zone
