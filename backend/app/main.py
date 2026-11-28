import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.calendar import router as calendar_router
from app.api.routes.checklist import router as checklist_router
from app.api.routes.mentor_applications import (
    admin_router as mentor_application_admin_router,
)
from app.api.routes.mentor_applications import router as mentor_applications_router
from app.api.routes.mentor_messages import router as mentor_messages_router
from app.api.routes.mentor_programs import router as mentor_programs_router
from app.api.routes.mentors import router as mentors_router
from app.api.routes.notes import router as notes_router
from app.api.routes.routines import router as routines_router
from app.core.config import get_settings
from app.core.errors import (
    AppError,
    app_error_handler,
    http_error_handler,
    validation_error_handler,
)
from app.infrastructure.db.session import SessionFactory
from app.services import admin as admin_service

logger = logging.getLogger("app.system")

app = FastAPI(title="Routine Manager API", version="0.1.0")

app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(StarletteHTTPException, http_error_handler)  # type: ignore[arg-type]

app.include_router(auth_router)
app.include_router(routines_router)
app.include_router(checklist_router)
app.include_router(notes_router)
app.include_router(calendar_router)
app.include_router(mentors_router)
app.include_router(mentor_messages_router)
app.include_router(mentor_programs_router)
app.include_router(mentor_applications_router)
app.include_router(mentor_application_admin_router)
app.include_router(admin_router)


@app.middleware("http")
async def record_failed_requests(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Record failed API requests in the system log (F-037).

    Logging happens in its own session after the response is produced, so a
    logging failure can never turn a handled error into a 500. Tests use an
    in-memory database whose schema the app does not own; they are skipped.
    """
    response = await call_next(request)

    if response.status_code < 400 or not request.url.path.startswith("/api/v1/"):
        return response
    if ":memory:" in get_settings().database_url:
        return response

    try:
        async with SessionFactory() as session:
            await admin_service.record_log(
                session,
                level="error" if response.status_code >= 500 else "warning",
                event="request.failed",
                message=(
                    f"{request.method} {request.url.path} "
                    f"responded {response.status_code}"
                ),
                status_code=response.status_code,
                method=request.method,
                path=request.url.path[:255],
            )
    except Exception:  # logging must never break a response
        logger.debug("could not record failed request", exc_info=True)

    return response


@app.get("/api/v1/healthz", tags=["health"])
@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
