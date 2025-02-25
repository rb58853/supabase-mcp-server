from supabase_mcp.exceptions import ValidationError


def validate_schema_name(schema_name: str) -> str:
    """Validate schema name.

    Rules:
    - Must be a string
    - Cannot be empty
    - Cannot contain spaces or special characters
    """
    if not isinstance(schema_name, str):
        raise ValidationError("Schema name must be a string")
    if not schema_name.strip():
        raise ValidationError("Schema name cannot be empty")
    if " " in schema_name:
        raise ValidationError("Schema name cannot contain spaces")
    return schema_name


def validate_table_name(table: str) -> str:
    """Validate table name.

    Rules:
    - Must be a string
    - Cannot be empty
    - Cannot contain spaces or special characters
    """
    if not isinstance(table, str):
        raise ValidationError("Table name must be a string")
    if not table.strip():
        raise ValidationError("Table name cannot be empty")
    if " " in table:
        raise ValidationError("Table name cannot contain spaces")
    return table


def validate_sql_query(query: str) -> str:
    """Validate SQL query.

    Rules:
    - Must be a string
    - Cannot be empty
    """
    if not isinstance(query, str):
        raise ValidationError("Query must be a string")
    if not query.strip():
        raise ValidationError("Query cannot be empty")

    return query


def validate_transaction_control(query: str) -> bool:
    """Validate if the query has transaction control.

    Rules:
    - Must be a string
    - Cannot be empty
    """
    return any(x in query.upper() for x in ["BEGIN", "COMMIT", "ROLLBACK"])
