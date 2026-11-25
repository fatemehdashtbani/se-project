"""Request and response schemas for calendar events (F-033)."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_TITLE_LENGTH = 200


def _clean_title(value: str) -> str:
    """Trim a title and reject one that is only whitespace."""
    title = value.strip()
    if not title:
        raise ValueError("title must not be blank")
    return title


class CalendarEventCreate(BaseModel):
    """Payload accepted by ``POST /api/v1/calendar-events``."""

    title: str = Field(max_length=MAX_TITLE_LENGTH)
    event_date: date

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return _clean_title(value)



class CalendarEventResponse(BaseModel):
    """Public representation of a calendar event."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    event_date: date
    created_at: datetime


class CalendarEventListResponse(BaseModel):
    """The caller's events inside the requested window."""

    items: list[CalendarEventResponse]
    total: int
