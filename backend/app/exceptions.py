from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.http_errors import APIError


def _error_body(detail: str, error_code: str) -> dict:
    return {"detail": detail, "error_code": error_code}


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(str(exc.detail), exc.error_code),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(detail, "http_error"),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    messages = []
    for error in errors:
        location = ".".join(str(part) for part in error.get("loc", []) if part != "body")
        message = error.get("msg", "Invalid value")
        if location:
            messages.append(f"{location}: {message}")
        else:
            messages.append(message)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_body("; ".join(messages), "validation_error"),
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    message = str(exc.orig) if exc.orig else str(exc)

    if "products_sku" in message or "sku" in message.lower():
        detail = "Product SKU must be unique"
        error_code = "duplicate_sku"
    elif "customers_email" in message or "email" in message.lower():
        detail = "Customer email must be unique"
        error_code = "duplicate_email"
    else:
        detail = "A database constraint was violated"
        error_code = "integrity_error"

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_error_body(detail, error_code),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body("An unexpected error occurred", "internal_error"),
    )
