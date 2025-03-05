from enum import Enum

from pydantic import BaseModel

from supabase_mcp.safety.core import OperationRiskLevel


class SQLQueryCategory(str, Enum):
    """Category of the SQL query tracked by the SQL validator"""

    DQL = "DQL"
    DML = "DML"
    DDL = "DDL"
    TCL = "TCL"
    DCL = "DCL"
    POSTGRES_SPECIFIC = "POSTGRES_SPECIFIC"
    OTHER = "OTHER"


class SQLQueryCommand(str, Enum):
    """Command of the SQL query tracked by the SQL validator"""

    # DQL Commands
    SELECT = "SELECT"

    # DML Commands
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    MERGE = "MERGE"

    # DDL Commands
    CREATE = "CREATE"
    ALTER = "ALTER"
    DROP = "DROP"
    TRUNCATE = "TRUNCATE"
    COMMENT = "COMMENT"
    RENAME = "RENAME"

    # DCL Commands
    GRANT = "GRANT"
    REVOKE = "REVOKE"

    # TCL Commands (for tracking, not query types)
    BEGIN = "BEGIN"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"
    SAVEPOINT = "SAVEPOINT"

    # PostgreSQL-specific Commands
    VACUUM = "VACUUM"
    ANALYZE = "ANALYZE"
    EXPLAIN = "EXPLAIN"
    COPY = "COPY"
    LISTEN = "LISTEN"
    NOTIFY = "NOTIFY"
    PREPARE = "PREPARE"
    EXECUTE = "EXECUTE"
    DEALLOCATE = "DEALLOCATE"

    # Other/Unknown
    UNKNOWN = "UNKNOWN"


class QueryValidationResult(BaseModel):
    """Result of the query validation."""

    category: SQLQueryCategory
    risk_level: OperationRiskLevel
    command: SQLQueryCommand
    object_type: str | None = None
    schema_name: str | None = None
    needs_migration: bool


class SQLBatchValidationResult(BaseModel):
    """Result of the batch validation."""

    statements: list[QueryValidationResult] = []
    highest_risk_level: OperationRiskLevel = OperationRiskLevel.LOW
    has_transaction_control: bool = False
    original_query: str

    def needs_migration(self) -> bool:
        """Check if any statement in the batch needs migration."""
        return any(stmt.needs_migration for stmt in self.statements)
