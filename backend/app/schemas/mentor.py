"""Request and response schemas for mentor collaboration (F-035)."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_HEADLINE_LENGTH = 120
MAX_MESSAGE_LENGTH = 4000
MAX_PROGRAM_TITLE_LENGTH = 200
MAX_PROGRAM_DESCRIPTION_LENGTH = 10_000

ProgramCategory = Literal["study", "sport", "life", "other"]


def _clean_text(value: str, *, field: str) -> str:
    """Trim a required text field and reject a whitespace-only value."""
    text = value.strip()
    if not text:
        raise ValueError(f"{field} must not be blank")
    return text


def _clean_optional_text(value: str | None) -> str | None:
    """Trim an optional text field, treating a blank value as absent."""
    if value is None:
        return None
    text = value.strip()
    return text or None


class MentorSummary(BaseModel):
    """A mentor as shown in the directory and selection card."""

    id: uuid.UUID
    name: str
    headline: str | None
    bio: str | None


class MentorListResponse(BaseModel):
    """Every account with the mentor role."""

    items: list[MentorSummary]
    total: int


class MentorSelectionRequest(BaseModel):
    """Payload accepted by ``PUT /api/v1/mentors/selected``."""

    mentor_id: uuid.UUID


class SelectedMentorResponse(BaseModel):
    """The caller's currently granted mentor, if any."""

    mentor: MentorSummary | None


class MentorClientSummary(BaseModel):
    """A client visible to a mentor, without contact details."""

    id: uuid.UUID
    name: str


class MentorClientListResponse(BaseModel):
    """Clients with an active grant for the calling mentor."""

    items: list[MentorClientSummary]
    total: int


class MentorMessageCreate(BaseModel):
    """Payload accepted by ``POST /api/v1/mentor-messages``.

    A user identifies the mentor (``mentor_id``); a mentor identifies the client
    (``client_id``). The sender is always the authenticated account.
    """

    mentor_id: uuid.UUID | None = None
    client_id: uuid.UUID | None = None
    body: str = Field(max_length=MAX_MESSAGE_LENGTH)

    @field_validator("body")
    @classmethod
    def normalize_body(cls, value: str) -> str:
        return _clean_text(value, field="body")


class MentorMessageResponse(BaseModel):
    """One stored message. ``sender_id`` lets the UI mark its own messages."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    body: str
    sender_id: uuid.UUID
    created_at: datetime


class MentorMessageListResponse(BaseModel):
    """A thread in chronological order."""

    items: list[MentorMessageResponse]
    total: int


class MentorProgramCreate(BaseModel):
    """Payload accepted by ``POST /api/v1/mentor-programs``."""

    client_id: uuid.UUID
    title: str = Field(max_length=MAX_PROGRAM_TITLE_LENGTH)
    description: str | None = Field(
        default=None, max_length=MAX_PROGRAM_DESCRIPTION_LENGTH
    )
    category: ProgramCategory

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return _clean_text(value, field="title")

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return _clean_optional_text(value)


class MentorProgramResponse(BaseModel):
    """A program a mentor sent; ``routine_id`` is set once it is adopted."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mentor_id: uuid.UUID
    title: str
    description: str | None
    category: str
    routine_id: uuid.UUID | None
    created_at: datetime


class MentorProgramListResponse(BaseModel):
    """Programs visible to the caller."""

    items: list[MentorProgramResponse]
    total: int
