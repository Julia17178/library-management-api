"""Centralized conversion of application failures into RFC 9457 responses."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    BusinessRuleError,
    DataConflictError,
    LibraryException,
    ResourceNotFoundError,
)

PROBLEM_BASE_URL = "https://library-management-api.local"


def problem_response(
    request: Request,
    *,
    problem_type: str,
    title: str,
    status_code: int,
    detail: str,
    errors: list[dict[str, Any]] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Create one consistent application/problem+json response."""
    body: dict[str, Any] = {
        "type": f"{PROBLEM_BASE_URL}{problem_type}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": request.url.path,
    }
    if errors is not None:
        body["errors"] = errors
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(body),
        media_type="application/problem+json",
        headers=headers,
    )


def handle_library_error(request: Request, exc: LibraryException) -> JSONResponse:
    """Convert domain/service exceptions into RFC 9457 responses."""
    if isinstance(exc, ResourceNotFoundError):
        return problem_response(
            request,
            problem_type="not-found",
            title="Not found",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    if isinstance(exc, (DataConflictError, BusinessRuleError)):
        return problem_response(
            request,
            problem_type="conflict",
            title="Conflict",
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    return problem_response(
        request,
        problem_type="application-error",
        title="Application error",
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )


def handle_http_exception(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Convert authentication, authorization, and framework HTTP errors."""
    known_problems = {
        status.HTTP_401_UNAUTHORIZED: ("unauthorized", "Unauthorized"),
        status.HTTP_403_FORBIDDEN: ("forbidden", "Forbidden"),
        status.HTTP_404_NOT_FOUND: ("not-found", "Not found"),
        status.HTTP_405_METHOD_NOT_ALLOWED: ("method-not-allowed", "Method not allowed"),
        status.HTTP_409_CONFLICT: ("conflict", "Conflict"),
    }
    problem_type, title = known_problems.get(
        exc.status_code, ("http-error", "HTTP error")
    )
    detail = (
        exc.detail
        if isinstance(exc.detail, str)
        else "The request could not be completed."
    )
    return problem_response(
        request,
        problem_type=problem_type,
        title=title,
        status_code=exc.status_code,
        detail=detail,
        headers=exc.headers,
    )


def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return FastAPI/Pydantic validation details in a stable error envelope."""
    return problem_response(
        request,
        problem_type="validation-error",
        title="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="One or more request values are invalid.",
        errors=exc.errors(),
    )


def handle_unexpected_error(request: Request, _exc: Exception) -> JSONResponse:
    """Return a safe response without exposing unexpected failure details."""
    return problem_response(
        request,
        problem_type="internal-server-error",
        title="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="The server encountered an unexpected condition.",
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register the shared HTTP representation policy on the application."""
    app.add_exception_handler(LibraryException, handle_library_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(Exception, handle_unexpected_error)
