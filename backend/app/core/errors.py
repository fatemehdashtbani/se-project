"""Stable error codes and handlers producing the AGENTS.md §6 error envelope."""

from collections.abc import Mapping
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

_ERROR_CODES: Mapping[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
}


class AppError(Exception):
    """A domain error that maps onto a stable HTTP status and code."""

    status_code: int = 400
    code: str = "APPLICATION_ERROR"
    message: str = "Request failed."

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)


def error_body(code: str, message: str) -> dict[str, dict[str, str]]:
    """Build the error envelope shared by every failing response."""
    return {"error": {"code": code, "message": message}}


def _first_validation_message(exc: RequestValidationError) -> str:
    errors: list[Any] = list(exc.errors())
    if not errors:
        return "Request validation failed."

    first = errors[0]
    location = ".".join(str(part) for part in first.get("loc", ()) if part != "body")
    detail = str(first.get("msg", "Invalid value"))
    return f"{location}: {detail}" if location else detail


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """Render an :class:`AppError` using the shared envelope."""
    return JSONResponse(
        status_code=exc.status_code, content=error_body(exc.code, exc.message)
    )


async def validation_error_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """Render FastAPI request validation failures in the shared envelope."""
    return JSONResponse(
        status_code=422,
        content=error_body("VALIDATION_ERROR", _first_validation_message(exc)),
    )


async def http_error_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Render framework HTTP errors (404, 405, ...) in the shared envelope."""
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(_ERROR_CODES.get(exc.status_code, "HTTP_ERROR"), message),
        headers=getattr(exc, "headers", None),
    )
