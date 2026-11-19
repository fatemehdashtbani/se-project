from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.auth import router as auth_router
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


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
