"""Request and response schemas for the admin panel (F-037)."""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AdminRole = Literal["user", "mentor", "admin"]
LogLevel = Literal["error", "warning", "info", "audit"]


def _required_text(value: str, *, field: str) -> str:
    """Trim a required text field and reject a whitespace-only value."""
    text = value.strip()
    if not text:
        raise ValueError(f"{field} must not be blank")
    return text


def _optional_text(value: str | None) -> str | None:
    """Trim an optional text field, treating a blank value as absent."""
    if value is None:
        return None
    return value.strip() or None


class DailyActivityPoint(BaseModel):
    """One day of the dashboard activity chart."""

    date: date
    signups: int
    routines: int
    active_users: int


class AdminDashboardResponse(BaseModel):
    """Platform-wide counters shown on the admin dashboard."""

    total_users: int
    active_users: int
    banned_users: int
    total_routines: int
    total_mentors: int
    pending_mentor_requests: int
    total_mentor_programs: int
    active_mentorships: int
    active_today: int
    total_templates: int
    total_categories: int
    total_broadcasts: int
    activity: list[DailyActivityPoint]


class AdminUserResponse(BaseModel):
    """One account as the admin user table shows it."""

    id: uuid.UUID
    email: str
    username: str | None
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    role: str
    timezone: str
    is_active: bool
    is_banned: bool
    created_at: datetime
    routines_count: int


class AdminUserListResponse(BaseModel):
    """A page of accounts."""

    items: list[AdminUserResponse]
    total: int


class AccountFlagRequest(BaseModel):
    """Enable/disable or ban/unban one account."""

    value: bool


class TemporaryPasswordResponse(BaseModel):
    """A freshly generated password, returned once to the administrator."""

    temporary_password: str


class AdminMentorResponse(BaseModel):
    """One active mentor with their load."""

    id: uuid.UUID
    name: str
    email: str
    headline: str | None
    bio: str | None
    clients_count: int
    created_at: datetime


class AdminMentorListResponse(BaseModel):
    """Every account holding the mentor role."""

    items: list[AdminMentorResponse]
    total: int


class MentorAssignmentRequest(BaseModel):
    """Assign a mentor to a user (grants consent on the user's behalf)."""

    user_id: uuid.UUID
    mentor_id: uuid.UUID


class ConversationSummary(BaseModel):
    """One mentor/client thread in the supervision view."""

    user_id: uuid.UUID
    user_name: str
    user_email: str
    mentor_id: uuid.UUID
    mentor_name: str
    mentor_email: str
    messages_count: int
    last_message_at: datetime | None


class ConversationListResponse(BaseModel):
    """Threads available for moderation."""

    items: list[ConversationSummary]
    total: int


class AdminMessageResponse(BaseModel):
    """One stored message, shown to an administrator for moderation."""

    id: uuid.UUID
    sender_id: uuid.UUID
    sender_name: str
    body: str
    created_at: datetime


class ConversationMessagesResponse(BaseModel):
    """The full thread between one mentor and one user."""

    user_id: uuid.UUID
    mentor_id: uuid.UUID
    items: list[AdminMessageResponse]


class TemplateCreate(BaseModel):
    """Payload for creating a routine template."""

    title: str = Field(max_length=200)
    description: str | None = Field(default=None)
    category: str | None = Field(default=None, max_length=60)
    duration_days: int | None = Field(default=None, ge=1, le=365)
    is_published: bool = True

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return _required_text(value, field="title")

    @field_validator("description", "category")
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        return _optional_text(value)


class TemplateUpdate(BaseModel):
    """Partially update a routine template."""

    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    category: str | None = Field(default=None, max_length=60)
    duration_days: int | None = Field(default=None, ge=1, le=365)
    is_published: bool | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        return None if value is None else _required_text(value, field="title")

    @field_validator("description", "category")
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        return _optional_text(value)


class TemplateResponse(BaseModel):
    """One routine template."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    category: str | None
    duration_days: int | None
    is_published: bool
    created_at: datetime
    updated_at: datetime


class TemplateListResponse(BaseModel):
    """Published and draft templates."""

    items: list[TemplateResponse]
    total: int


class CategoryCreate(BaseModel):
    """Payload for defining a habit category."""

    name: str = Field(max_length=60)
    description: str | None = Field(default=None, max_length=255)
    color: str = Field(default="#7c3aed", max_length=20)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _required_text(value, field="name")

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return _optional_text(value)


class CategoryUpdate(BaseModel):
    """Partially update a habit category."""

    name: str | None = Field(default=None, max_length=60)
    description: str | None = Field(default=None, max_length=255)
    color: str | None = Field(default=None, max_length=20)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return None if value is None else _required_text(value, field="name")

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return _optional_text(value)


class CategoryResponse(BaseModel):
    """One habit category."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    color: str
    created_at: datetime


class CategoryListResponse(BaseModel):
    """Every habit category."""

    items: list[CategoryResponse]
    total: int


class BroadcastCreate(BaseModel):
    """Payload for sending a platform-wide announcement."""

    title: str = Field(max_length=200)
    body: str = Field(max_length=5_000)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return _required_text(value, field="title")

    @field_validator("body")
    @classmethod
    def normalize_body(cls, value: str) -> str:
        return _required_text(value, field="body")


class BroadcastResponse(BaseModel):
    """One broadcast announcement."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    body: str
    audience: str
    recipients: int
    created_at: datetime


class BroadcastListResponse(BaseModel):
    """Sent announcements, newest first."""

    items: list[BroadcastResponse]
    total: int


class SystemLogResponse(BaseModel):
    """One record in the system log viewer."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    level: str
    event: str
    message: str
    status_code: int | None
    method: str | None
    path: str | None
    created_at: datetime


class SystemLogListResponse(BaseModel):
    """A page of system logs."""

    items: list[SystemLogResponse]
    total: int
