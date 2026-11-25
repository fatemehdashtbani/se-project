"""Request and response schemas for personal notes (F-033)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_TITLE_LENGTH = 200
MAX_CONTENT_LENGTH = 10000


def _clean_title(value: str) -> str:
    """Trim a title and reject one that is only whitespace."""
    title = value.strip()
    if not title:
        raise ValueError("title must not be blank")
    return title


class NoteCreate(BaseModel):
    """Payload accepted by ``POST /api/v1/notes``."""

    title: str = Field(max_length=MAX_TITLE_LENGTH)
    content: str = Field(default="", max_length=MAX_CONTENT_LENGTH)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return _clean_title(value)

    @field_validator("content")
    @classmethod
    def trim_content(cls, value: str) -> str:
        return value.strip()


class NoteUpdate(BaseModel):
    """Partial update payload for ``PUT /api/v1/notes/{note_id}``."""

    title: str | None = Field(default=None, max_length=MAX_TITLE_LENGTH)
    content: str | None = Field(default=None, max_length=MAX_CONTENT_LENGTH)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("title must be a string")
        return _clean_title(value)

    @field_validator("content")
    @classmethod
    def reject_null_content(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("content must be a string")
        return value.strip()

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "NoteUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        return self


class NoteResponse(BaseModel):
    """Public representation of a note."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    """The caller's notes and their total count."""

    items: list[NoteResponse]
    total: int
