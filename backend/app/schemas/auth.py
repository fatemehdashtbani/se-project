"""Request and response schemas for authentication."""

import re
import uuid
from datetime import datetime
from zoneinfo import available_timezones

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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


def normalize_person_name(value: str) -> str:
    """Trim a first or last name and reject one that is only whitespace."""
    name = value.strip()
    if not name:
        raise ValueError("name must not be blank")
    return name


def normalize_phone_number(value: str) -> str:
    """Drop the spaces and dashes people type, then check the digits."""
    phone = re.sub(r"[\s-]", "", value)
    if not PHONE_PATTERN.fullmatch(phone):
        raise ValueError("invalid phone number")
    return phone


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
        return normalize_person_name(value)

    @field_validator("phone_number")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        return normalize_phone_number(value)


class LoginRequest(BaseModel):
    """Payload accepted by ``POST /api/v1/auth/login``.

    ``identifier`` is either an email address or a phone number, so the same
    form can serve both login modes. The password is only required to be
    present: rejecting short passwords here would leak the registration policy
    and turn a mistyped password into a 422.
    """

    identifier: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)
    # When true the session survives a browser restart; when false both session
    # cookies are non-persistent and end with the browser session (F-002).
    remember_me: bool = False

    @field_validator("identifier")
    @classmethod
    def strip_identifier(cls, value: str) -> str:
        identifier = value.strip()
        if not identifier:
            raise ValueError("identifier must not be blank")
        return identifier


class ForgotPasswordRequest(BaseModel):
    """Payload accepted by ``POST /api/v1/auth/forgot-password``."""

    email: str = Field(max_length=320)

    @field_validator("email")
    @classmethod
    def normalize(cls, value: str) -> str:
        return normalize_email(value)


class ResetPasswordRequest(BaseModel):
    """Payload accepted by ``POST /api/v1/auth/reset-password`` (F-022)."""

    token: str = Field(min_length=1, max_length=200)
    new_password: str = Field(
        min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH
    )

    @field_validator("token")
    @classmethod
    def strip_token(cls, value: str) -> str:
        token = value.strip()
        if not token:
            raise ValueError("token must not be blank")
        return token


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


class ProfileUpdateRequest(BaseModel):
    """Partial payload accepted by ``PUT /api/v1/auth/me`` (F-031).

    Only the fields present in the body are applied, so a form that sends all
    three keeps working and a future inline edit can send one. An explicit null
    is rejected for the same reason as ``RoutineUpdate.title``: the columns hold
    real profile values, and clearing them is not a supported operation.
    """

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(default=None, max_length=20)

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("name must be a string")
        return normalize_person_name(value)

    @field_validator("phone_number")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("phone_number must be a string")
        return normalize_phone_number(value)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "ProfileUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        return self


class ChangePasswordRequest(BaseModel):
    """Payload accepted by ``PUT /api/v1/auth/me/password`` (F-031)."""

    current_password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)
    new_password: str = Field(
        min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH
    )


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
