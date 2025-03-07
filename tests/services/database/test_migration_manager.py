import re

import pytest

from supabase_mcp.services.database.migration_manager import MigrationManager
from supabase_mcp.services.database.sql.validator import SQLValidator


@pytest.fixture
def validator() -> SQLValidator:
    """Create a SQLValidator instance for testing."""
    return SQLValidator()


@pytest.fixture
def sample_ddl_queries() -> dict[str, str]:
    """Sample DDL (CREATE, ALTER, DROP) queries for testing."""
    return {
        "create_table": "CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT, email TEXT UNIQUE)",
        "create_table_with_schema": "CREATE TABLE public.users (id SERIAL PRIMARY KEY, name TEXT, email TEXT UNIQUE)",
        "create_table_custom_schema": "CREATE TABLE app.users (id SERIAL PRIMARY KEY, name TEXT, email TEXT UNIQUE)",
        "alter_table": "ALTER TABLE users ADD COLUMN active BOOLEAN DEFAULT false",
        "drop_table": "DROP TABLE users",
        "truncate_table": "TRUNCATE TABLE users",
        "create_index": "CREATE INDEX idx_user_email ON users (email)",
    }


@pytest.fixture
def sample_edge_cases() -> dict[str, str]:
    """Sample edge cases for testing."""
    return {
        "with_comments": "SELECT * FROM users; -- This is a comment\n/* Multi-line\ncomment */",
        "quoted_identifiers": 'SELECT * FROM "user table" WHERE "first name" = \'John\'',
        "special_characters": "SELECT * FROM users WHERE name LIKE 'O''Brien%'",
        "schema_qualified": "SELECT * FROM public.users",
        "with_dollar_quotes": "SELECT $$This is a dollar-quoted string with 'quotes'$$ AS message",
    }


@pytest.fixture
def sample_multiple_statements() -> dict[str, str]:
    """Sample SQL with multiple statements for testing batch processing."""
    return {
        "multiple_ddl": "CREATE TABLE users (id SERIAL PRIMARY KEY); CREATE TABLE posts (id SERIAL PRIMARY KEY);",
        "mixed_with_migration": "SELECT * FROM users; CREATE TABLE logs (id SERIAL PRIMARY KEY);",
        "only_select": "SELECT * FROM users;",
    }


class TestMigrationManager:
    """Tests for the MigrationManager class."""

    def test_generate_descriptive_name_with_default_schema(
        self, validator: SQLValidator, sample_ddl_queries: dict[str, str]
    ):
        """Test generating a descriptive name with default schema."""
        # Use the create_table query from fixtures (no explicit schema)
        result = validator.validate_query(sample_ddl_queries["create_table"])

        # Create a migration manager and generate a name
        mm = MigrationManager()
        name = mm.generate_descriptive_name(result)

        # Check that the name follows the expected format with default schema
        assert name == "create_public_users"

    def test_generate_descriptive_name_with_explicit_schema(
        self, validator: SQLValidator, sample_ddl_queries: dict[str, str]
    ):
        """Test generating a descriptive name with explicit schema."""
        # Use the create_table_with_schema query from fixtures
        result = validator.validate_query(sample_ddl_queries["create_table_with_schema"])

        # Create a migration manager and generate a name
        mm = MigrationManager()
        name = mm.generate_descriptive_name(result)

        # Check that the name follows the expected format with explicit schema
        assert name == "create_public_users"

    def test_generate_descriptive_name_with_custom_schema(
        self, validator: SQLValidator, sample_ddl_queries: dict[str, str]
    ):
        """Test generating a descriptive name with custom schema."""
        # Use the create_table_custom_schema query from fixtures
        result = validator.validate_query(sample_ddl_queries["create_table_custom_schema"])

        # Create a migration manager and generate a name
        mm = MigrationManager()
        name = mm.generate_descriptive_name(result)

        # Check that the name follows the expected format with custom schema
        assert name == "create_app_users"

    def test_generate_descriptive_name_with_multiple_statements(
        self, validator: SQLValidator, sample_multiple_statements: dict[str, str]
    ):
        """Test generating a descriptive name with multiple statements."""
        # Use the multiple_ddl query from fixtures
        result = validator.validate_query(sample_multiple_statements["multiple_ddl"])

        # Create a migration manager and generate a name
        mm = MigrationManager()
        name = mm.generate_descriptive_name(result)

        # Check that the name is based on the first non-TCL statement that needs migration
        assert name == "create_public_users"

    def test_generate_descriptive_name_with_mixed_statements(
        self, validator: SQLValidator, sample_multiple_statements: dict[str, str]
    ):
        """Test generating a descriptive name with mixed statements."""
        # Use the mixed_with_migration query from fixtures
        result = validator.validate_query(sample_multiple_statements["mixed_with_migration"])

        # Create a migration manager and generate a name
        mm = MigrationManager()
        name = mm.generate_descriptive_name(result)

        # Check that the name is based on the first statement that needs migration (skipping SELECT)
        assert name == "create_public_logs"

    def test_generate_descriptive_name_with_no_migration_statements(
        self, validator: SQLValidator, sample_multiple_statements: dict[str, str]
    ):
        """Test generating a descriptive name with no statements that need migration."""
        # Use the only_select query from fixtures (renamed from only_tcl)
        result = validator.validate_query(sample_multiple_statements["only_select"])

        # Create a migration manager and generate a name
        mm = MigrationManager()
        name = mm.generate_descriptive_name(result)

        # Check that a generic name is generated
        assert re.match(r"migration_\w+", name)
