from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

_STATUS_BY_EXCEPTION = {
    NotFoundError: 404,
    ConflictError: 409,
    ValidationError: 422,
    UnauthorizedError: 401,
    ForbiddenError: 403,
}


def register_error_handlers(app: FastAPI) -> None:
    for exc_type, status_code in _STATUS_BY_EXCEPTION.items():

        def _handler(request: Request, exc: Exception, status_code: int = status_code):
            return JSONResponse(status_code=status_code, content={"detail": str(exc)})

        app.add_exception_handler(exc_type, _handler)
