"""Request and response schemas for mentor applications (F-036)."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_EXPERTISE_LENGTH = 200
MAX_BIO_LENGTH = 5_000
MAX_DOCUMENTS_LENGTH = 2_000

ApplicationStatus = Literal["pending", "approved", "rejected"]


def _clean_required(value: str, *, field: str) -> str:
    """Trim a required text field and reject a whitespace-only value."""
    text = value.strip()
    if not text:
        raise ValueError(f"{field} must not be blank")
    return text


def _clean_optional(value: str | None) -> str | None:
    """Trim an optional text field, treating a blank value as absent."""
    if value is None:
        return None
    return value.strip() or None


class MentorApplicationCreate(BaseModel):
    """Payload accepted by ``POST /api/v1/mentor-applications``."""

    expertise: str = Field(max_length=MAX_EXPERTISE_LENGTH)
    bio: str = Field(max_length=MAX_BIO_LENGTH)
    documents: str | None = Field(default=None, max_length=MAX_DOCUMENTS_LENGTH)

    @field_validator("expertise")
    @classmethod
    def normalize_expertise(cls, value: str) -> str:
        return _clean_required(value, field="expertise")

    @field_validator("bio")
    @classmethod
    def normalize_bio(cls, value: str) -> str:
        return _clean_required(value, field="bio")

    @field_validator("documents")
    @classmethod
    def normalize_documents(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class MentorApplicationResponse(BaseModel):
    """One application as its owner sees it."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    expertise: str
    bio: str
    documents: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    reviewed_at: datetime | None


class MyMentorApplicationResponse(BaseModel):
    """The caller's current application, if one was ever submitted."""

    application: MentorApplicationResponse | None


class AdminMentorApplicationResponse(MentorApplicationResponse):
    """An application in the admin queue, with the applicant's identity."""

    applicant_name: str
    applicant_email: str


class MentorApplicationListResponse(BaseModel):
    """Applications visible to an administrator."""

    items: list[AdminMentorApplicationResponse]
    total: int
