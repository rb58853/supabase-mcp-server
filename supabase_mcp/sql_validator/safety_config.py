"""Defines the safety configuration for different SQL categories and commands"""

from typing import Any

from supabase_mcp.sql_validator.models import SQLQueryCategory, SQLQuerySafetyLevel

STATEMENT_CONFIG = {
    # DQL - all SAFE, no migrations
    "SelectStmt": {
        "category": SQLQueryCategory.DQL,
        "safety_level": SQLQuerySafetyLevel.SAFE,
        "needs_migration": False,
    },
    # "CopyStmt": {  # COPY TO variant (read)
    #     "category": SQLQueryCategory.DQL,
    #     "safety_level": SQLQuerySafetyLevel.SAFE,
    #     "needs_migration": False,
    # },
    "ExplainStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.SAFE,
        "needs_migration": False,
    },
    # DML - all WRITE, no migrations
    "InsertStmt": {
        "category": SQLQueryCategory.DML,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": False,
    },
    "UpdateStmt": {
        "category": SQLQueryCategory.DML,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": False,
    },
    "DeleteStmt": {
        "category": SQLQueryCategory.DML,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": False,
    },
    "MergeStmt": {
        "category": SQLQueryCategory.DML,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": False,
    },
    # "CopyStmt": {  # COPY FROM variant (write)
    #     "category": SQLQueryCategory.DML,
    #     "safety_level": SQLQuerySafetyLevel.WRITE,
    #     "needs_migration": False,
    # },
    # DDL - mix of WRITE and DESTRUCTIVE, need migrations
    "CreateStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "CreateTableAsStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "CreateSchemaStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "CreateExtensionStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "AlterTableStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "AlterDomainStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "CreateFunctionStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "IndexStmt": {  # CREATE INDEX
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "CreateTrigStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "ViewStmt": {  # CREATE VIEW
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "CommentStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    # DESTRUCTIVE DDL - need migrations and confirmation
    "DropStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.DESTRUCTIVE,
        "needs_migration": True,
    },
    "TruncateStmt": {
        "category": SQLQueryCategory.DDL,
        "safety_level": SQLQuerySafetyLevel.DESTRUCTIVE,
        "needs_migration": True,
    },
    # DCL - WRITE, need migrations
    "GrantStmt": {
        "category": SQLQueryCategory.DCL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "GrantRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "RevokeStmt": {
        "category": SQLQueryCategory.DCL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "RevokeRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "CreateRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "AlterRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": True,
    },
    "DropRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "safety_level": SQLQuerySafetyLevel.DESTRUCTIVE,
        "needs_migration": True,
    },
    # TCL - SAFE, no migrations
    "TransactionStmt": {
        "category": SQLQueryCategory.TCL,
        "safety_level": SQLQuerySafetyLevel.SAFE,
        "needs_migration": False,
    },
    # PostgreSQL-specific
    "VacuumStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": False,
    },
    "AnalyzeStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.SAFE,
        "needs_migration": False,
    },
    "ClusterStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": False,
    },
    "CheckPointStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": False,
    },
    "PrepareStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.SAFE,
        "needs_migration": False,
    },
    "ExecuteStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.WRITE,  # Could be SAFE or WRITE based on prepared statement
        "needs_migration": False,
    },
    "DeallocateStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.SAFE,
        "needs_migration": False,
    },
    "ListenStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.SAFE,
        "needs_migration": False,
    },
    "NotifyStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "safety_level": SQLQuerySafetyLevel.WRITE,
        "needs_migration": False,
    },
}


# Functions for more complex determinations
def classify_statement(stmt_type: str, stmt_node: Any) -> dict[str, Any]:
    """Get classification rules for a given statement type from our config."""
    config = STATEMENT_CONFIG.get(
        stmt_type,
        {
            "category": SQLQueryCategory.OTHER,
            "safety_level": SQLQuerySafetyLevel.WRITE,  # Default to write for unknown
            "needs_migration": False,
        },
    )

    # Special case: CopyStmt can be read or write
    if stmt_type == "CopyStmt" and stmt_node:
        # Check if it's COPY TO (read) or COPY FROM (write)
        if hasattr(stmt_node, "is_from") and not stmt_node.is_from:
            # COPY TO - it's a read operation
            config["category"] = SQLQueryCategory.DQL
            config["safety_level"] = SQLQuerySafetyLevel.SAFE
        else:
            # COPY FROM - it's a write operation
            config["category"] = SQLQueryCategory.DML
            config["safety_level"] = SQLQuerySafetyLevel.WRITE

    # Other special cases can be added here

    return config
