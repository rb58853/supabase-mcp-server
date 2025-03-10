from pathlib import Path

from supabase_mcp.logger import logger


class SQLLoader:
    """Responsible for loading SQL queries from files."""

    # Path to SQL files directory
    SQL_DIR = Path(__file__).parent / "queries"

    @classmethod
    def load_sql(cls, filename: str) -> str:
        """
        Load SQL from a file in the sql directory.

        Args:
            filename: Name of the SQL file (with or without .sql extension)

        Returns:
            str: The SQL query from the file

        Raises:
            FileNotFoundError: If the SQL file doesn't exist
        """
        # Ensure the filename has .sql extension
        if not filename.endswith(".sql"):
            filename = f"{filename}.sql"

        file_path = cls.SQL_DIR / filename

        if not file_path.exists():
            logger.error(f"SQL file not found: {file_path}")
            raise FileNotFoundError(f"SQL file not found: {file_path}")

        with open(file_path) as f:
            sql = f.read().strip()
            logger.debug(f"Loaded SQL file: {filename} ({len(sql)} chars)")
            return sql

    @classmethod
    def get_schemas_query(cls) -> str:
        """Get a query to list all schemas."""
        return cls.load_sql("get_schemas")

    @classmethod
    def get_tables_query(cls, schema_name: str) -> str:
        """Get a query to list all tables in a schema."""
        query = cls.load_sql("get_tables")
        return query.replace("{schema_name}", schema_name)

    @classmethod
    def get_table_schema_query(cls, schema_name: str, table: str) -> str:
        """Get a query to get the schema of a table."""
        query = cls.load_sql("get_table_schema")
        return query.replace("{schema_name}", schema_name).replace("{table}", table)

    @classmethod
    def get_migrations_query(
        cls, limit: int = 50, offset: int = 0, name_pattern: str = "", include_full_queries: bool = False
    ) -> str:
        """Get a query to list migrations."""
        query = cls.load_sql("get_migrations")
        return (
            query.replace("{limit}", str(limit))
            .replace("{offset}", str(offset))
            .replace("{name_pattern}", name_pattern)
            .replace("{include_full_queries}", str(include_full_queries).lower())
        )

    @classmethod
    def get_init_migrations_query(cls) -> str:
        """Get a query to initialize the migrations schema and table."""
        return cls.load_sql("init_migrations")

    @classmethod
    def get_create_migration_query(cls, version: str, name: str, statements: str) -> str:
        """Get a query to create a migration.

        Args:
            version: The migration version (timestamp)
            name: The migration name
            statements: The SQL statements (escaped)

        Returns:
            str: The SQL query to create a migration
        """
        query = cls.load_sql("create_migration")
        return query.replace("{version}", version).replace("{name}", name).replace("{statements}", statements)
