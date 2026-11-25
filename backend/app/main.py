from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.auth import router as auth_router
from app.api.routes.calendar import router as calendar_router
from app.api.routes.checklist import router as checklist_router
from app.api.routes.mentor_messages import router as mentor_messages_router
from app.api.routes.mentor_programs import router as mentor_programs_router
from app.api.routes.mentors import router as mentors_router
from app.api.routes.notes import router as notes_router
from app.api.routes.routines import router as routines_router
from app.core.errors import (
    AppError,
    app_error_handler,
    http_error_handler,
    validation_error_handler,
)

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


@app.get("/api/v1/healthz", tags=["health"])
@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
