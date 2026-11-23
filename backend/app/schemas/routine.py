"""Request and response schemas for routine CRUD (F-005)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_TITLE_LENGTH = 200


def _clean_title(value: str) -> str:
    """Trim a title and reject one that is only whitespace."""
    title = value.strip()
    if not title:
        raise ValueError("title must not be blank")
    return title


def _clean_description(value: str | None) -> str | None:
    """Trim a description, treating a blank string as absent."""
    if value is None:
        return None

    description = value.strip()
    return description or None


class RoutineCreate(BaseModel):
    """Payload accepted by ``POST /api/v1/routines`` (FR-F005-001)."""

    title: str = Field(max_length=MAX_TITLE_LENGTH)
    description: str | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return _clean_title(value)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return _clean_description(value)


class RoutineUpdate(BaseModel):
    """Partial update payload for ``PUT /api/v1/routines/{routine_id}``.

    Only the fields present in the request body are applied (FR-F005-003), so an
    empty body is rejected instead of silently behaving as a no-op.
    """

    title: str | None = Field(default=None, max_length=MAX_TITLE_LENGTH)
    description: str | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str:
        # An explicit null would clear a NOT NULL column. Absent fields never
        # reach this validator, so only a client-sent null is rejected here.
        if value is None:
            raise ValueError("title must be a string")
        return _clean_title(value)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return _clean_description(value)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "RoutineUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        return self


class RoutineResponse(BaseModel):
    """Public representation of a routine.

    The owner is implied by the session, so ``user_id`` and ``deleted_at`` are
    deliberately not exposed.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoutineListResponse(BaseModel):
    """One page of the caller's routines plus their total count."""

    items: list[RoutineResponse]
    total: int
