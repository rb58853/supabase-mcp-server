import datetime
import random
import re

from supabase_mcp.logger import logger
from supabase_mcp.services.database.sql.models import QueryValidationResults

# List of simple words to use for random uniqueness in migration names
RANDOM_WORDS = [
    "apple",
    "banana",
    "cherry",
    "date",
    "elder",
    "fig",
    "grape",
    "honey",
    "iris",
    "jade",
    "kiwi",
    "lemon",
    "mango",
    "navy",
    "olive",
    "peach",
    "quartz",
    "ruby",
    "silver",
    "teal",
    "umber",
    "violet",
    "wheat",
    "yellow",
    "zinc",
]


class MigrationManager:
    """Responsible for preparing migration scripts without executing them."""

    def prepare_migration(self, name: str, query: str) -> str:
        """
        Prepare a migration script without executing it.

        Args:
            name: A descriptive name for the migration
            query: The SQL query to include in the migration

        Returns:
            Complete SQL query to create the migration
        """
        if not query:
            raise ValueError("Cannot create migration: No SQL query provided")

        # Generate migration version (timestamp)
        version = self.generate_date()

        # Sanitize and format the migration name
        migration_name = self.generate_name(name)

        # Escape single quotes in the query for SQL safety
        escaped_query = query.replace("'", "''")

        # Create the complete migration query with values directly embedded
        migration_query = f"""
        INSERT INTO supabase_migrations.schema_migrations
        (version, name, statements)
        VALUES ('{version}', '{migration_name}', ARRAY['{escaped_query}']);
        """

        logger.info(f"Prepared migration: {version}_{migration_name}")

        # Return the complete query
        return migration_query

    def generate_name(self, name: str) -> str:
        """
        Generate a standardized name for a migration script.

        Args:
            name: Raw migration name

        Returns:
            str: Sanitized migration name
        """
        # Remove special characters and replace spaces with underscores
        sanitized_name = re.sub(r"[^\w\s]", "", name).lower()
        sanitized_name = re.sub(r"\s+", "_", sanitized_name)

        # Ensure the name is not too long (max 100 chars)
        if len(sanitized_name) > 100:
            sanitized_name = sanitized_name[:100]

        return sanitized_name

    def generate_descriptive_name(self, validation_result: QueryValidationResults) -> str:
        """
        Generate a descriptive name for a migration based on the validation result.

        Skips transaction control statements and finds the first non-TCL statement
        that requires migration.

        Format: command_schema_object
        Example: create_public_users

        Args:
            validation_result: Validation result for a batch of SQL statements

        Returns:
            str: Descriptive migration name
        """
        # Find the first non-TCL statement that needs migration
        statement = None
        for stmt in validation_result.statements:
            # Skip transaction control statements
            if stmt.category.value == "TCL":
                continue

            if stmt.needs_migration:
                statement = stmt
                break

        # If no statement found (unlikely), use a generic name
        if not statement:
            return f"migration_{random.choice(RANDOM_WORDS)}"

        # 1. Command (always available)
        command = statement.command.value.lower()

        # 2. Schema name (if available)
        schema_name = statement.schema_name.lower() if statement.schema_name else "public"

        # 3. Object name (if available)
        object_name = statement.object_type.lower() if statement.object_type else "unknown"

        # Combine all parts
        name = f"{command}_{schema_name}_{object_name}"

        # Sanitize the name (remove special characters, etc.)
        return self.generate_name(name)

    def generate_date(self) -> str:
        """
        Generate a timestamp for a migration script in the format YYYYMMDDHHMMSS.

        Returns:
            str: Timestamp string
        """
        now = datetime.datetime.now()
        return now.strftime("%Y%m%d%H%M%S")
