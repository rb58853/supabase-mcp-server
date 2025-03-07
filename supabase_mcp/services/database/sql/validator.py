from typing import Any

from pglast.parser import ParseError, parse_sql

from supabase_mcp.exceptions import ValidationError
from supabase_mcp.logger import logger
from supabase_mcp.services.database.sql.models import (
    QueryValidationResults,
    SQLQueryCategory,
    SQLQueryCommand,
    ValidatedStatement,
)
from supabase_mcp.services.safety.safety_configs import SQLSafetyConfig


class SQLValidator:
    """SQL validator class that is based on pglast library.

    Responsible for:
    - SQL query syntax validation
    - SQL query categorization"""

    def __init__(self, safety_config: SQLSafetyConfig | None = None) -> None:
        self.safety_config = safety_config or SQLSafetyConfig()

    def validate_schema_name(self, schema_name: str) -> str:
        """Validate schema name.

        Rules:
        - Must be a string
        - Cannot be empty
        - Cannot contain spaces or special characters
        """
        if not schema_name.strip():
            raise ValidationError("Schema name cannot be empty")
        if " " in schema_name:
            raise ValidationError("Schema name cannot contain spaces")
        return schema_name

    def validate_table_name(self, table: str) -> str:
        """Validate table name.

        Rules:
        - Must be a string
        - Cannot be empty
        - Cannot contain spaces or special characters
        """
        if not table.strip():
            raise ValidationError("Table name cannot be empty")
        if " " in table:
            raise ValidationError("Table name cannot contain spaces")
        return table

    def basic_query_validation(self, query: str) -> str:
        """Validate SQL query.

        Rules:
        - Must be a string
        - Cannot be empty
        """
        if not query.strip():
            raise ValidationError("Query cannot be empty")
        return query

    @classmethod
    def validate_transaction_control(cls, query: str) -> bool:
        """Check if the query contains transaction control statements.

        Args:
            query: SQL query string

        Returns:
            bool: True if the query contains any transaction control statements
        """
        return any(x in query.upper() for x in ["BEGIN", "COMMIT", "ROLLBACK"])

    def validate_query(self, sql_query: str) -> QueryValidationResults:
        """
        Identify the type of SQL query using PostgreSQL's parser.

        Args:
            sql_query: A SQL query string to parse

        Returns:
            QueryValidationResults: A validation result object containing information about the SQL statements
        Raises:
            ValidationError: If the query is not valid or contains TCL statements
        """
        try:
            # Validate raw input
            sql_query = self.basic_query_validation(sql_query)

            # Parse the SQL using PostgreSQL's parser
            parse_tree = parse_sql(sql_query)
            if parse_tree is None:
                logger.debug("No statements found in the query")
            # logger.debug(f"Parse tree generated with {parse_tree} statements")

            # Validate statements
            result = self.validate_statements(original_query=sql_query, parse_tree=parse_tree)

            # Check if the query contains transaction control statements and reject them
            for statement in result.statements:
                if statement.category == SQLQueryCategory.TCL:
                    logger.warning(f"Transaction control statement detected: {statement.command}")
                    raise ValidationError(
                        "Transaction control statements (BEGIN, COMMIT, ROLLBACK) are not allowed. "
                        "Queries will be automatically wrapped in transactions by the system."
                    )

            return result
        except ParseError as e:
            logger.exception(f"SQL syntax error: {str(e)}")
            raise ValidationError(f"SQL syntax error: {str(e)}") from e
        except ValidationError:
            # let it propagate
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during SQL validation: {str(e)}")
            raise ValidationError(f"Unexpected error during SQL validation: {str(e)}") from e

    def _map_to_command(self, stmt_type: str) -> SQLQueryCommand:
        """Map a pglast statement type to our SQLQueryCommand enum."""

        mapping = {
            # DQL Commands
            "SelectStmt": SQLQueryCommand.SELECT,
            # DML Commands
            "InsertStmt": SQLQueryCommand.INSERT,
            "UpdateStmt": SQLQueryCommand.UPDATE,
            "DeleteStmt": SQLQueryCommand.DELETE,
            "MergeStmt": SQLQueryCommand.MERGE,
            # DDL Commands
            "CreateStmt": SQLQueryCommand.CREATE,
            "AlterTableStmt": SQLQueryCommand.ALTER,
            "DropStmt": SQLQueryCommand.DROP,
            "TruncateStmt": SQLQueryCommand.TRUNCATE,
            "CommentStmt": SQLQueryCommand.COMMENT,
            "RenameStmt": SQLQueryCommand.RENAME,
            # DCL Commands
            "GrantStmt": SQLQueryCommand.GRANT,
            "RevokeStmt": SQLQueryCommand.REVOKE,
            # TCL Commands
            "TransactionStmt": SQLQueryCommand.BEGIN,  # Will need refinement for different transaction types
            # PostgreSQL-specific Commands
            "VacuumStmt": SQLQueryCommand.VACUUM,
            "ExplainStmt": SQLQueryCommand.EXPLAIN,
            "CopyStmt": SQLQueryCommand.COPY,
            "ListenStmt": SQLQueryCommand.LISTEN,
            "NotifyStmt": SQLQueryCommand.NOTIFY,
            "PrepareStmt": SQLQueryCommand.PREPARE,
            "ExecuteStmt": SQLQueryCommand.EXECUTE,
            "DeallocateStmt": SQLQueryCommand.DEALLOCATE,
        }

        # Try to map the statement type, default to UNKNOWN
        return mapping.get(stmt_type, SQLQueryCommand.UNKNOWN)

    def validate_statements(self, original_query: str, parse_tree: Any) -> QueryValidationResults:
        """Validate the statements in the parse tree.

        Args:
            parse_tree: The parse tree to validate

        Returns:
            SQLBatchValidationResult: A validation result object containing information about the SQL statements
        Raises:
            ValidationError: If the query is not valid
        """
        result = QueryValidationResults(original_query=original_query)

        if parse_tree is None:
            return result

        try:
            for stmt in parse_tree:
                if not hasattr(stmt, "stmt"):
                    continue

                stmt_node = stmt.stmt
                stmt_type = stmt_node.__class__.__name__
                logger.debug(f"Processing statement node type: {stmt_type}")
                # logger.debug(f"DEBUGGING stmt_node: {stmt_node}")
                logger.debug(f"DEBUGGING stmt_node.stmt_location: {stmt.stmt_location}")

                # Extract the object type if available
                object_type = None
                schema_name = None
                if hasattr(stmt_node, "relation") and stmt_node.relation is not None:
                    if hasattr(stmt_node.relation, "relname"):
                        object_type = stmt_node.relation.relname
                    if hasattr(stmt_node.relation, "schemaname"):
                        schema_name = stmt_node.relation.schemaname
                # For statements with 'relations' list (like TRUNCATE)
                elif hasattr(stmt_node, "relations") and stmt_node.relations:
                    for relation in stmt_node.relations:
                        if hasattr(relation, "relname"):
                            object_type = relation.relname
                        if hasattr(relation, "schemaname"):
                            schema_name = relation.schemaname
                        break

                # Get classification for this statement type
                classification = self.safety_config.classify_statement(stmt_type, stmt_node)
                logger.debug(
                    f"Statement category classified as: {classification.get('category', 'UNKNOWN')} - risk level: {classification.get('risk_level', 'UNKNOWN')}"
                )
                logger.debug(f"DEBUGGING QUERY EXTRACTION LOCATION: {stmt.stmt_location} - {stmt.stmt_len}")

                # Create validation result
                query_result = ValidatedStatement(
                    category=classification["category"],
                    command=self._map_to_command(stmt_type),
                    risk_level=classification["risk_level"],
                    needs_migration=classification["needs_migration"],
                    object_type=object_type,
                    schema_name=schema_name,
                    query=original_query[stmt.stmt_location : stmt.stmt_location + stmt.stmt_len]
                    if hasattr(stmt, "stmt_location") and hasattr(stmt, "stmt_len")
                    else None,
                )
                # logger.debug(f"Isolated query: {query_result.query}")
                logger.debug(
                    "Query validation result:",
                    {
                        "statement_category": query_result.category,
                        "risk_level": query_result.risk_level,
                        "needs_migration": query_result.needs_migration,
                        "object_type": query_result.object_type,
                        "schema_name": query_result.schema_name,
                        "query": query_result.query,
                    },
                )

                # Add result to the batch
                result.statements.append(query_result)

                # Update highest risk level
                if query_result.risk_level > result.highest_risk_level:
                    result.highest_risk_level = query_result.risk_level
                    logger.debug(f"Updated batch validation result to: {query_result.risk_level}")
            if len(result.statements) == 0:
                logger.debug("No valid statements found in the query")
                raise ValidationError("No queries were parsed - please check correctness of your query")
            logger.debug(
                f"Validated a total of {len(result.statements)} with the highest risk level of: {result.highest_risk_level}"
            )
            return result

        except AttributeError as e:
            # Handle attempting to access missing attributes in the parse tree
            raise ValidationError(f"Error accessing parse tree structure: {str(e)}") from e
        except KeyError as e:
            # Handle missing keys in classification dictionary
            raise ValidationError(f"Missing classification key: {str(e)}") from e


validator3000 = SQLValidator(SQLSafetyConfig())

if __name__ == "__main__":
    print("\n=== TESTING SQL VALIDATOR WITH INVALID SYNTAX ===\n")

    # # Test Case 1: Missing FROM clause in SELECT
    # print("\n--- Test Case 1: Missing FROM clause ---")
    # try:
    #     print("Running: validator3000.validate_query('SELECT name, email WHERE id = 1')")
    #     result = validator3000.validate_query("SELECT name, email WHERE id = 1")
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error caught: {str(e)}")

    # # Test Case 2: Invalid table name with special characters
    # print("\n--- Test Case 2: Invalid table name with special characters ---")
    # try:
    #     print("Running: validator3000.validate_query('SELECT * FROM users$table')")
    #     result = validator3000.validate_query("SELECT * FROM users$table")
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error caught: {str(e)}")

    # # Test Case 3: Unclosed string literal
    # print("\n--- Test Case 3: Unclosed string literal ---")
    # try:
    #     print('Running: validator3000.validate_query("SELECT * FROM users WHERE name = \'John")')
    #     result = validator3000.validate_query("SELECT * FROM users WHERE name = 'John")
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error caught: {str(e)}")

    # # Test Case 4: Invalid SQL keyword
    # print("\n--- Test Case 4: Invalid SQL keyword ---")
    # try:
    #     print("Running: validator3000.validate_query('SELEKT * FROM users')")
    #     result = validator3000.validate_query("SELEKT * FROM users")
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error caught: {str(e)}")

    # # Test Case 5: Semi-valid - Missing semicolon in multi-statement
    # print("\n--- Test Case 5: Semi-valid - Missing semicolon in multi-statement ---")
    # try:
    #     print("""Running: validator3000.validate_query('''
    # BEGIN;
    # CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT)
    # INSERT INTO test (name) VALUES ('test');
    # COMMIT;
    # ''')""")
    #     result = validator3000.validate_query("""
    # BEGIN;
    # CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT)
    # INSERT INTO test (name) VALUES ('test');
    # COMMIT;
    # """)
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error caught: {str(e)}")

    # print("\n=== END OF INVALID SYNTAX TESTS ===\n")

    # Additional incorrect SQL queries
#     print("\n=== TESTING MORE INCORRECT SQL QUERIES ===\n")

#     # Test Case 6: Missing closing parenthesis
#     print("\n--- Test Case 6: Missing closing parenthesis ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT * FROM users WHERE id IN (1, 2, 3')")
#         result = validator3000.validate_query("SELECT * FROM users WHERE id IN (1, 2, 3")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Test Case 7: Invalid JOIN syntax
#     print("\n--- Test Case 7: Invalid JOIN syntax ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT * FROM users JOIN posts ON')")
#         result = validator3000.validate_query("SELECT * FROM users JOIN posts ON")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Test Case 8: Incorrect GROUP BY syntax
#     print("\n--- Test Case 8: Incorrect GROUP BY syntax ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT count(*), name FROM users GROUP')")
#         result = validator3000.validate_query("SELECT count(*), name FROM users GROUP")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Test Case 9: Invalid column reference in ORDER BY
#     print("\n--- Test Case 9: Invalid column reference in ORDER BY ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT name FROM users ORDER BY age, ')")
#         result = validator3000.validate_query("SELECT name FROM users ORDER BY age, ")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Test Case 10: Incorrect CASE statement
#     print("\n--- Test Case 10: Incorrect CASE statement ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT CASE WHEN id > 10 THEN \"High\" FROM users')")
#         result = validator3000.validate_query('SELECT CASE WHEN id > 10 THEN "High" FROM users')
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Test Case 11: Invalid date format
#     print("\n--- Test Case 11: Invalid date format ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT * FROM users WHERE created_at > \"2023-13-45\"')")
#         result = validator3000.validate_query('SELECT * FROM users WHERE created_at > "2023-13-45"')
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Test Case 12: Incorrect use of aggregate function
#     print("\n--- Test Case 12: Incorrect use of aggregate function ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT name, SUM(id) FROM users')")
#         result = validator3000.validate_query("SELECT name, SUM(id) FROM users")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Test Case 13: Invalid table alias
#     print("\n--- Test Case 13: Invalid table alias ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT u. FROM users u')")
#         result = validator3000.validate_query("SELECT u. FROM users u")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Test Case 14: Incorrect subquery
#     print("\n--- Test Case 14: Incorrect subquery ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT * FROM users WHERE id IN (SELECT FROM posts)')")
#         result = validator3000.validate_query("SELECT * FROM users WHERE id IN (SELECT FROM posts)")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Test Case 15: Invalid use of DISTINCT
#     print("\n--- Test Case 15: Invalid use of DISTINCT ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT DISTINCT, name FROM users')")
#         result = validator3000.validate_query("SELECT DISTINCT, name FROM users")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     print("\n=== END OF ADDITIONAL INCORRECT SQL QUERIES ===\n")

#     # Original examples
#     print("\n=== RUNNING ORIGINAL SQL VALIDATOR EXAMPLES ===\n")

#     # Empty query
#     print("\n--- Empty Query ---")
#     try:
#         print("Running: validator3000.validate_query('')")
#         result = validator3000.validate_query("")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Query with a space in the table name
#     print("\n--- Query with space in table name ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT * FROM new users WHERE name = \"John Doe\"')")
#         result = validator3000.validate_query("SELECT * FROM new users WHERE name = 'John Doe'")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Comment
#     print("\n--- Comment Example ---")
#     try:
#         print("Running: validator3000.validate_query('-- This is a comment')")
#         result = validator3000.validate_query("-- This is a comment")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Copy
#     print("\n--- Copy Example ---")
#     try:
#         print("Running: validator3000.validate_query('COPY users TO STDOUT')")
#         result = validator3000.validate_query("COPY users TO STDOUT")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # DQL Example
#     print("\n--- DQL Example ---")
#     try:
#         print("Running: validator3000.validate_query('SELECT * FROM users WHERE email LIKE \"%@example.com\"')")
#         result = validator3000.validate_query("SELECT * FROM users WHERE email LIKE '%@example.com'")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # DDL Examples
#     print("\n--- DDL Examples ---")
#     try:
#         print("Running: validator3000.validate_query('CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT)')")
#         result = validator3000.validate_query("CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT)")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     try:
#         print("Running: validator3000.validate_query('ALTER TABLE users ADD COLUMN phone TEXT')")
#         result = validator3000.validate_query("ALTER TABLE users ADD COLUMN phone TEXT")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     try:
#         print("Running: validator3000.validate_query('DROP TABLE test')")
#         result = validator3000.validate_query("DROP TABLE test")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     try:
#         print("Running: validator3000.validate_query('TRUNCATE TABLE logs')")
#         result = validator3000.validate_query("TRUNCATE TABLE logs")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # DML Examples
#     print("\n--- DML Examples ---")
#     try:
#         print(
#             'Running: validator3000.validate_query(\'INSERT INTO users (name, email) VALUES ("John", "john@example.com")\')'
#         )
#         result = validator3000.validate_query("INSERT INTO users (name, email) VALUES ('John', 'john@example.com')")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     try:
#         print("Running: validator3000.validate_query('UPDATE users SET name = \"Jane\" WHERE id = 1')")
#         result = validator3000.validate_query("UPDATE users SET name = 'Jane' WHERE id = 1")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     try:
#         print("Running: validator3000.validate_query('DELETE FROM users WHERE id = 1')")
#         result = validator3000.validate_query("DELETE FROM users WHERE id = 1")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # DCL Examples
#     print("\n--- DCL Examples ---")
#     try:
#         print("Running: validator3000.validate_query('GRANT SELECT ON users TO read_only_role')")
#         result = validator3000.validate_query("GRANT SELECT ON users TO read_only_role")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     try:
#         print("Running: validator3000.validate_query('REVOKE ALL ON users FROM public')")
#         result = validator3000.validate_query("REVOKE ALL ON users FROM public")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Transaction Examples
#     print("\n--- Transaction Examples ---")
#     try:
#         print("Running: validator3000.validate_query('BEGIN')")
#         result = validator3000.validate_query("BEGIN")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     try:
#         print("Running: validator3000.validate_query('COMMIT')")
#         result = validator3000.validate_query("COMMIT")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     try:
#         print("Running: validator3000.validate_query('ROLLBACK')")
#         result = validator3000.validate_query("ROLLBACK")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # PostgreSQL-specific Examples
#     print("\n--- PostgreSQL-specific Examples ---")
#     try:
#         print("Running: validator3000.validate_query('VACUUM users')")
#         result = validator3000.validate_query("VACUUM users")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     try:
#         print("Running: validator3000.validate_query('EXPLAIN SELECT * FROM users')")
#         result = validator3000.validate_query("EXPLAIN SELECT * FROM users")
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # Complex Example with Multiple Statements
#     print("\n--- Complex Example ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# BEGIN;
# CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT);
# INSERT INTO test (name) VALUES ('test');
# COMMIT;
# ''')""")
#         result = validator3000.validate_query("""
# BEGIN;
# CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT);
# INSERT INTO test (name) VALUES ('test');
# COMMIT;
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # EDGE CASES AND COMPLEX SCENARIOS
#     print("\n=== EDGE CASES AND COMPLEX SCENARIOS ===\n")

#     # 1. Multiple statements without transaction
#     print("\n--- Edge Case 1: Multiple statements without transaction ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# CREATE TABLE test2 (id SERIAL PRIMARY KEY, name TEXT);
# INSERT INTO test2 (name) VALUES ('test');
# ''')""")
#         result = validator3000.validate_query("""
# CREATE TABLE test2 (id SERIAL PRIMARY KEY, name TEXT);
# INSERT INTO test2 (name) VALUES ('test');
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # 2. Nested transactions
#     print("\n--- Edge Case 2: Nested transactions ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# BEGIN;
#   INSERT INTO users (name) VALUES ('outer');
#   BEGIN;
#     INSERT INTO users (name) VALUES ('inner');
#   COMMIT;
#   UPDATE users SET name = 'updated' WHERE name = 'outer';
# COMMIT;
# ''')""")
#         result = validator3000.validate_query("""
# BEGIN;
#   INSERT INTO users (name) VALUES ('outer');
#   BEGIN;
#     INSERT INTO users (name) VALUES ('inner');
#   COMMIT;
#   UPDATE users SET name = 'updated' WHERE name = 'outer';
# COMMIT;
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # 3. Transaction with SAVEPOINT
#     print("\n--- Edge Case 3: Transaction with SAVEPOINT ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# BEGIN;
#   INSERT INTO users (name) VALUES ('test1');
#   SAVEPOINT sp1;
#   INSERT INTO users (name) VALUES ('test2');
#   ROLLBACK TO SAVEPOINT sp1;
#   INSERT INTO users (name) VALUES ('test3');
# COMMIT;
# ''')""")
#         result = validator3000.validate_query("""
# BEGIN;
#   INSERT INTO users (name) VALUES ('test1');
#   SAVEPOINT sp1;
#   INSERT INTO users (name) VALUES ('test2');
#   ROLLBACK TO SAVEPOINT sp1;
#   INSERT INTO users (name) VALUES ('test3');
# COMMIT;
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # 4. Mixed read and write operations
#     print("\n--- Edge Case 4: Mixed read and write operations ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# BEGIN;
#   INSERT INTO users (name) VALUES ('test');
#   SELECT * FROM users WHERE name = 'test';
#   UPDATE users SET name = 'updated' WHERE name = 'test';
# COMMIT;
# ''')""")
#         result = validator3000.validate_query("""
# BEGIN;
#   INSERT INTO users (name) VALUES ('test');
#   SELECT * FROM users WHERE name = 'test';
#   UPDATE users SET name = 'updated' WHERE name = 'test';
# COMMIT;
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # 5. Complex CTE with multiple operations
#     print("\n--- Edge Case 5: Complex CTE with multiple operations ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# WITH inserted AS (
#   INSERT INTO users (name) VALUES ('from_cte') RETURNING id, name
# ), updated AS (
#   UPDATE users SET name = 'updated_from_cte' WHERE id IN (SELECT id FROM inserted) RETURNING id, name
# )
# SELECT * FROM inserted UNION ALL SELECT * FROM updated;
# ''')""")
#         result = validator3000.validate_query("""
# WITH inserted AS (
#   INSERT INTO users (name) VALUES ('from_cte') RETURNING id, name
# ), updated AS (
#   UPDATE users SET name = 'updated_from_cte' WHERE id IN (SELECT id FROM inserted) RETURNING id, name
# )
# SELECT * FROM inserted UNION ALL SELECT * FROM updated;
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # 7. Multiple DDL operations in one transaction
#     print("\n--- Edge Case 7: Multiple DDL operations in one transaction ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# BEGIN;
#   CREATE TABLE parent (id SERIAL PRIMARY KEY, name TEXT);
#   CREATE TABLE child (
#     id SERIAL PRIMARY KEY,
#     parent_id INTEGER REFERENCES parent(id),
#     name TEXT
#   );
#   CREATE INDEX idx_parent_name ON parent(name);
#   CREATE INDEX idx_child_name ON child(name);
#   ALTER TABLE parent ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
# COMMIT;
# ''')""")
#         result = validator3000.validate_query("""
# BEGIN;
#   CREATE TABLE parent (id SERIAL PRIMARY KEY, name TEXT);
#   CREATE TABLE child (
#     id SERIAL PRIMARY KEY,
#     parent_id INTEGER REFERENCES parent(id),
#     name TEXT
#   );
#   CREATE INDEX idx_parent_name ON parent(name);
#   CREATE INDEX idx_child_name ON child(name);
#   ALTER TABLE parent ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
# COMMIT;
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # 8. Transaction with procedural language
#     print("\n--- Edge Case 8: Transaction with procedural language ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# BEGIN;
#   CREATE OR REPLACE FUNCTION increment_counter() RETURNS TRIGGER AS $$
#   BEGIN
#     NEW.counter := OLD.counter + 1;
#     RETURN NEW;
#   END;
#   $$ LANGUAGE plpgsql;

#   CREATE TRIGGER update_counter BEFORE UPDATE ON counters
#   FOR EACH ROW EXECUTE FUNCTION increment_counter();
# COMMIT;
# ''')""")
#         result = validator3000.validate_query("""
# BEGIN;
#   CREATE OR REPLACE FUNCTION increment_counter() RETURNS TRIGGER AS $$
#   BEGIN
#     NEW.counter := OLD.counter + 1;
#     RETURN NEW;
#   END;
#   $$ LANGUAGE plpgsql;

#   CREATE TRIGGER update_counter BEFORE UPDATE ON counters
#   FOR EACH ROW EXECUTE FUNCTION increment_counter();
# COMMIT;
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # 9. Transaction with RLS policy
#     print("\n--- Edge Case 9: Transaction with RLS policy ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# BEGIN;
#   CREATE TABLE private_data (id SERIAL PRIMARY KEY, user_id UUID, content TEXT);
#   ALTER TABLE private_data ENABLE ROW LEVEL SECURITY;
#   CREATE POLICY user_policy ON private_data
#     USING (user_id = current_setting('app.current_user_id')::UUID);
# COMMIT;
# ''')""")
#         result = validator3000.validate_query("""
# BEGIN;
#   CREATE TABLE private_data (id SERIAL PRIMARY KEY, user_id UUID, content TEXT);
#   ALTER TABLE private_data ENABLE ROW LEVEL SECURITY;
#   CREATE POLICY user_policy ON private_data
#     USING (user_id = current_setting('app.current_user_id')::UUID);
# COMMIT;
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     # 10. Transaction with multiple schemas
#     print("\n--- Edge Case 10: Transaction with multiple schemas ---")
#     try:
#         print("""Running: validator3000.validate_query('''
# BEGIN;
#   CREATE SCHEMA IF NOT EXISTS app;
#   CREATE SCHEMA IF NOT EXISTS auth;

#   CREATE TABLE app.users (id SERIAL PRIMARY KEY, name TEXT);
#   CREATE TABLE auth.credentials (
#     user_id INTEGER REFERENCES app.users(id),
#     password_hash TEXT
#   );
# COMMIT;
# ''')""")
#         result = validator3000.validate_query("""
# BEGIN;
#   CREATE SCHEMA IF NOT EXISTS app;
#   CREATE SCHEMA IF NOT EXISTS auth;

#   CREATE TABLE app.users (id SERIAL PRIMARY KEY, name TEXT);
#   CREATE TABLE auth.credentials (
#     user_id INTEGER REFERENCES app.users(id),
#     password_hash TEXT
#   );
# COMMIT;
# """)
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error caught: {str(e)}")

#     print("\n=== END OF SQL VALIDATOR EXAMPLES ===\n")
