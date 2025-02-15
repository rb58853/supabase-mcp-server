from src.exceptions import ValidationError


def validate_schema_name(schema: str) -> str:
    """Validate schema name.

    Rules:
    - Must be a string
    - Cannot be empty
    - Cannot contain spaces or special characters
    """
    if not isinstance(schema, str):
        raise ValidationError("Schema name must be a string")
    if not schema.strip():
        raise ValidationError("Schema name cannot be empty")
    if " " in schema:
        raise ValidationError("Schema name cannot contain spaces")
    return schema


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
    - Must start with SELECT (read-only)
    """
    if not isinstance(query, str):
        raise ValidationError("Query must be a string")
    if not query.strip():
        raise ValidationError("Query cannot be empty")
    if not query.strip().upper().startswith("SELECT"):
        raise ValidationError("Only SELECT queries are allowed")
    return query
