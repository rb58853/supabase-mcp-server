class DatabaseError(Exception):
    """Base class for database-related errors."""

    pass


class ConnectionError(DatabaseError):
    """Raised when connection to database fails."""

    pass


class PermissionError(DatabaseError):
    """Raised when user lacks required privileges."""

    pass


class QueryError(DatabaseError):
    """Raised when query execution fails."""

    pass


class TimeoutError(DatabaseError):
    """Raised when a query execution exceeds the specified timeout."""

    pass


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


class SafetyError(Exception):
    """Operation not allowed due to safety rules"""

    pass


class APIError(Exception):
    """Base class for API-related errors"""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict | None = None,
    ):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class APIConnectionError(APIError):
    """Failed to connect to API"""

    pass


class APIResponseError(APIError):
    """Failed to process API response"""

    pass


class APIClientError(APIError):
    """Client-side error (4xx)"""

    pass


class APIServerError(APIError):
    """Server-side error (5xx)"""

    pass


class UnexpectedError(APIError):
    """Unexpected error during API operation"""

    pass
