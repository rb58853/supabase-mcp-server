"""Defines the safety configuration for different SQL categories and commands"""

from typing import Any

from supabase_mcp.safety.core import OperationRiskLevel, SafetyConfigBase
from supabase_mcp.sql_validator.models import (
    QueryValidationResults,
    SQLQueryCategory,
)

# SQL statement configuration with direct risk level mapping
STATEMENT_CONFIG = {
    # DQL - all LOW risk, no migrations
    "SelectStmt": {
        "category": SQLQueryCategory.DQL,
        "risk_level": OperationRiskLevel.LOW,
        "needs_migration": False,
    },
    "ExplainStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.LOW,
        "needs_migration": False,
    },
    # DML - all MEDIUM risk, no migrations
    "InsertStmt": {
        "category": SQLQueryCategory.DML,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": False,
    },
    "UpdateStmt": {
        "category": SQLQueryCategory.DML,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": False,
    },
    "DeleteStmt": {
        "category": SQLQueryCategory.DML,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": False,
    },
    "MergeStmt": {
        "category": SQLQueryCategory.DML,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": False,
    },
    # DDL - mix of MEDIUM and HIGH risk, need migrations
    "CreateStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "CreateTableAsStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "CreateSchemaStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "CreateExtensionStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "AlterTableStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "AlterDomainStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "CreateFunctionStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "IndexStmt": {  # CREATE INDEX
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "CreateTrigStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "ViewStmt": {  # CREATE VIEW
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "CommentStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    # DESTRUCTIVE DDL - HIGH risk, need migrations and confirmation
    "DropStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.HIGH,
        "needs_migration": True,
    },
    "TruncateStmt": {
        "category": SQLQueryCategory.DDL,
        "risk_level": OperationRiskLevel.HIGH,
        "needs_migration": True,
    },
    # DCL - MEDIUM risk, need migrations
    "GrantStmt": {
        "category": SQLQueryCategory.DCL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "GrantRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "RevokeStmt": {
        "category": SQLQueryCategory.DCL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "RevokeRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "CreateRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "AlterRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": True,
    },
    "DropRoleStmt": {
        "category": SQLQueryCategory.DCL,
        "risk_level": OperationRiskLevel.HIGH,
        "needs_migration": True,
    },
    # TCL - LOW risk, no migrations
    "TransactionStmt": {
        "category": SQLQueryCategory.TCL,
        "risk_level": OperationRiskLevel.LOW,
        "needs_migration": False,
    },
    # PostgreSQL-specific
    "VacuumStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": False,
    },
    "AnalyzeStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.LOW,
        "needs_migration": False,
    },
    "ClusterStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": False,
    },
    "CheckPointStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": False,
    },
    "PrepareStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.LOW,
        "needs_migration": False,
    },
    "ExecuteStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.MEDIUM,  # Could be LOW or MEDIUM based on prepared statement
        "needs_migration": False,
    },
    "DeallocateStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.LOW,
        "needs_migration": False,
    },
    "ListenStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.LOW,
        "needs_migration": False,
    },
    "NotifyStmt": {
        "category": SQLQueryCategory.POSTGRES_SPECIFIC,
        "risk_level": OperationRiskLevel.MEDIUM,
        "needs_migration": False,
    },
}


# Functions for more complex determinations
def classify_statement(stmt_type: str, stmt_node: Any) -> dict[str, Any]:
    """Get classification rules for a given statement type from our config."""
    config = STATEMENT_CONFIG.get(
        stmt_type,
        # if not found - default to MEDIUM risk
        {
            "category": SQLQueryCategory.OTHER,
            "risk_level": OperationRiskLevel.MEDIUM,  # Default to MEDIUM risk for unknown
            "needs_migration": False,
        },
    )

    # Special case: CopyStmt can be read or write
    if stmt_type == "CopyStmt" and stmt_node:
        # Check if it's COPY TO (read) or COPY FROM (write)
        if hasattr(stmt_node, "is_from") and not stmt_node.is_from:
            # COPY TO - it's a read operation (LOW risk)
            config["category"] = SQLQueryCategory.DQL
            config["risk_level"] = OperationRiskLevel.LOW
        else:
            # COPY FROM - it's a write operation (MEDIUM risk)
            config["category"] = SQLQueryCategory.DML
            config["risk_level"] = OperationRiskLevel.MEDIUM

    # Other special cases can be added here

    return config


class SQLSafetyConfig(SafetyConfigBase[QueryValidationResults]):
    """Safety configuration for SQL operations."""

    def get_risk_level(self, operation: QueryValidationResults) -> OperationRiskLevel:
        """Get the risk level for an SQL batch operation.

        Args:
            operation: The SQL batch validation result to check

        Returns:
            The highest risk level found in the batch
        """
        # Simply return the highest risk level that's already tracked in the batch
        return operation.highest_risk_level
