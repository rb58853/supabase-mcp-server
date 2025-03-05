"""API-related error classes.

This module defines error classes for API operations.
"""

from typing import Any


class APIError(Exception):
    """Base class for all API-related errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class APIClientError(APIError):
    """Error raised for client errors (4xx)."""

    def __init__(self, message: str, status_code: int, response_body: dict[str, Any] | None = None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class APIConnectionError(APIError):
    """Error raised for connection issues."""

    def __init__(self, message: str):
        super().__init__(message)


class APIResponseError(APIError):
    """Error raised for response parsing errors."""

    def __init__(self, message: str, status_code: int, response_body: dict[str, Any] | None = None):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class UnexpectedError(APIError):
    """Error raised for unexpected errors."""

    def __init__(self, message: str):
        super().__init__(message)


class SafetyError(APIError):
    """Error raised for safety violations."""

    def __init__(self, message: str):
        super().__init__(message)
