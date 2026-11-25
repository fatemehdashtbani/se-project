"""Request and response schemas for the personal checklist (F-033)."""

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


class ChecklistItemCreate(BaseModel):
    """Payload accepted by ``POST /api/v1/checklist-items``."""

    title: str = Field(max_length=MAX_TITLE_LENGTH)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return _clean_title(value)


class ChecklistItemUpdate(BaseModel):
    """Partial update payload for ``PUT /api/v1/checklist-items/{item_id}``."""

    title: str | None = Field(default=None, max_length=MAX_TITLE_LENGTH)
    is_done: bool | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("title must be a string")
        return _clean_title(value)

    @field_validator("is_done")
    @classmethod
    def reject_null_is_done(cls, value: bool | None) -> bool:
        if value is None:
            raise ValueError("is_done must be a boolean")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "ChecklistItemUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        return self


class ChecklistItemResponse(BaseModel):
    """Public representation of a checklist item."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    is_done: bool
    created_at: datetime
    updated_at: datetime


class ChecklistListResponse(BaseModel):
    """The caller's checklist plus the done/total counters the page shows."""

    items: list[ChecklistItemResponse]
    total: int
    done: int
