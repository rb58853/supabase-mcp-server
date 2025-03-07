from typing import Any


class DatabaseError(Exception):
    """Base class for database-related errors."""

    pass


class ConnectionError(DatabaseError):
    """Raised when a database connection fails."""

    pass


class PermissionError(DatabaseError):
    """Raised when a database operation is not permitted."""

    pass


class QueryError(DatabaseError):
    """Raised when a database query fails."""

    pass


class TimeoutError(DatabaseError):
    """Raised when a database operation times out."""

    pass


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


class SafetyError(Exception):
    """Raised when a safety check fails."""

    pass


class OperationNotAllowedError(SafetyError):
    """Raised when an operation is not allowed in the current safety mode."""

    pass


class ConfirmationRequiredError(SafetyError):
    """Raised when a user needs to confirm destructive SQL operation"""

    pass


class APIError(Exception):
    """Base class for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
    ):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class APIConnectionError(APIError):
    """Raised when an API connection fails."""

    pass


class PythonSDKError(Exception):
    """Raised when a Python SDK operation fails."""

    pass


class APIResponseError(APIError):
    """Raised when an API response is invalid."""

    pass


class APIClientError(APIError):
    """Raised when an API client error occurs."""

    pass


class APIServerError(APIError):
    """Raised when an API server error occurs."""

    pass


class UnexpectedError(APIError):
    """Raised when an unexpected error occurs."""

    pass
