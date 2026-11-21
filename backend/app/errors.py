from __future__ import annotations

from typing import Any


class ApiError(Exception):
    """An error that must be rendered using the API contract error shape."""

    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def error_payload(code: str, message: str) -> dict[str, Any]:
    """Build { "error": { "code": ..., "message": ... } }."""
    return {"error": {"code": code, "message": message}}


def not_found(message: str) -> ApiError:
    return ApiError(code="NOT_FOUND", message=message, status_code=404)


def validation_error(message: str) -> ApiError:
    return ApiError(code="VALIDATION_ERROR", message=message, status_code=422)


def chatbot_unreachable(message: str) -> ApiError:
    return ApiError(code="CHATBOT_UNREACHABLE", message=message, status_code=502)


def internal_error(message: str = "Internal server error") -> ApiError:
    return ApiError(code="INTERNAL_ERROR", message=message, status_code=500)
