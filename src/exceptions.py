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


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass
