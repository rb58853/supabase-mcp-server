import datetime
import random
import re

from supabase_mcp.logger import logger
from supabase_mcp.sql_validator.models import SQLBatchValidationResult

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

    def prepare_migration(self, name: str, query: str) -> tuple[str, tuple[str, str, list[str]]]:
        """
        Prepare a migration script without executing it.

        Args:
            name: A descriptive name for the migration
            query: The SQL query to include in the migration

        Returns:
            Tuple containing:
            - SQL query to create the migration
            - Parameters for the query
        """
        if not query:
            raise ValueError("Cannot create migration: No SQL query provided")

        # Generate migration version (timestamp)
        version = self.generate_date()

        # Sanitize and format the migration name
        migration_name = self.generate_name(name)

        # Create the migration query
        migration_query = """
        BEGIN;
        INSERT INTO supabase_migrations.schema_migrations
        (version, name, statements)
        VALUES (%s, %s, %s);
        COMMIT;
        """

        # For the migration, we store the original query as a single statement
        # This preserves the transaction control and exact SQL
        statements = [query]

        logger.info(f"Prepared migration: {version}_{migration_name}")

        # Return the query and parameters
        return migration_query, (version, migration_name, statements)

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

    def generate_descriptive_name(self, validation_result: SQLBatchValidationResult) -> str:
        """
        Generate a descriptive name for a migration based on the validation result.

        Skips transaction control statements and finds the first non-TCL statement
        that requires migration.

        Format: command_objecttype_category_randomword
        Example: create_users_ddl_banana

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

        # 2. Object type (if available)
        object_part = statement.object_type.lower() if statement.object_type else "unknown"

        # 3. Category (always available)
        category = statement.category.value.lower()

        # 4. Random word for uniqueness
        random_word = random.choice(RANDOM_WORDS)

        # Combine all parts
        name = f"{command}_{object_part}_{category}_{random_word}"

        return name

    def generate_date(self) -> str:
        """
        Generate a timestamp for a migration script in the format YYYYMMDDHHMMSS.

        Returns:
            str: Timestamp string
        """
        now = datetime.datetime.now()
        return now.strftime("%Y%m%d%H%M%S")
