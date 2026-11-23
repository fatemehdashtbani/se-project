"""Request and response schemas for authentication."""

import re
import uuid
from datetime import datetime
from zoneinfo import available_timezones

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_PATTERN = re.compile(r"^\+?[0-9]{7,15}$")
USERNAME_PATTERN = re.compile(r"^[^\s]{3,50}$")

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


def normalize_email(value: str) -> str:
    """Trim, lowercase, and reject malformed addresses."""
    email = value.strip().lower()
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("invalid email format")
    return email


class RegisterRequest(BaseModel):
    """Payload accepted by ``POST /api/v1/auth/register``.

    The profile fields are required for new accounts. They are stored as
    nullable columns so users registered before the redesign keep working.
    """

    email: str = Field(max_length=320)
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH
    )
    username: str = Field(min_length=3, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone_number: str = Field(min_length=7, max_length=20)

    @field_validator("email")
    @classmethod
    def normalize(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        """Trim the username and reject embedded whitespace."""
        username = value.strip()
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValueError("invalid username")
        return username

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("name must not be blank")
        return name

    @field_validator("phone_number")
    @classmethod
    def normalize_phone_number(cls, value: str) -> str:
        """Drop the spaces and dashes people type, then check the digits."""
        phone = re.sub(r"[\s-]", "", value)
        if not PHONE_PATTERN.fullmatch(phone):
            raise ValueError("invalid phone number")
        return phone


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
    username: str | None
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    created_at: datetime


class MeResponse(BaseModel):
    """Profile returned by ``GET /api/v1/auth/me`` (SPEC FR-F019-006)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    timezone: str
    username: str | None
    first_name: str | None
    last_name: str | None
    phone_number: str | None


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
