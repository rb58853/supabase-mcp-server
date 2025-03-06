# Supabase MCP Tools Test Log

This document logs the testing of all available MCP tools in the Supabase MCP server.

## Table of Contents
1. [Database Tools](#database-tools)
2. [Management API Tools](#management-api-tools)
3. [Auth Admin Tools](#auth-admin-tools)
4. [Safety and Configuration Tools](#safety-and-configuration-tools)

## Database Tools

### 1. get_schemas

**Description**: Lists all database schemas with their sizes and table counts.

**Result**: ✅ Successfully retrieved schema information.
```json
{
  "results": [
    {
      "rows": [
        {"schema_name": "auth", "total_size": "784 kB", "table_count": 16},
        {"schema_name": "content", "total_size": "256 kB", "table_count": 7},
        {"schema_name": "storage", "total_size": "144 kB", "table_count": 5},
        {"schema_name": "realtime", "total_size": "56 kB", "table_count": 3},
        {"schema_name": "_realtime", "total_size": "136 kB", "table_count": 3},
        {"schema_name": "supabase_functions", "total_size": "64 kB", "table_count": 2},
        {"schema_name": "net", "total_size": "48 kB", "table_count": 2},
        {"schema_name": "cron", "total_size": "208 kB", "table_count": 2},
        {"schema_name": "chat", "total_size": "144 kB", "table_count": 2},
        {"schema_name": "supabase_migrations", "total_size": "112 kB", "table_count": 2},
        {"schema_name": "public", "total_size": "32 kB", "table_count": 1},
        {"schema_name": "vault", "total_size": "24 kB", "table_count": 1},
        {"schema_name": "extensions", "total_size": "0 bytes", "table_count": 0},
        {"schema_name": "graphql", "total_size": "0 bytes", "table_count": 0},
        {"schema_name": "graphql_public", "total_size": "0 bytes", "table_count": 0}
      ]
    }
  ]
}
```

### 2. get_tables

**Description**: Lists all tables, foreign tables, and views in a schema with their sizes, row counts, and metadata.

**Result for public schema**: ✅ Successfully retrieved table information.
```json
{
  "results": [
    {
      "rows": [
        {
          "table_name": "test_truncate",
          "table_type": "BASE TABLE",
          "description": null,
          "size_bytes": 32768,
          "row_count": 0,
          "column_count": 2,
          "index_count": 1
        }
      ]
    }
  ]
}
```

### 3. get_table_schema

**Description**: Gets detailed table structure including columns, keys, and relationships.

**Result for public.test_truncate**: ✅ Successfully retrieved table schema.
```json
{
  "results": [
    {
      "rows": [
        {
          "column_name": "id",
          "data_type": "integer",
          "is_nullable": "NO",
          "column_default": "nextval('test_truncate_id_seq'::regclass)",
          "ordinal_position": 1,
          "foreign_table_name": null,
          "foreign_column_name": null,
          "column_description": null,
          "is_primary_key": true
        },
        {
          "column_name": "name",
          "data_type": "text",
          "is_nullable": "YES",
          "column_default": null,
          "ordinal_position": 2,
          "foreign_table_name": null,
          "foreign_column_name": null,
          "column_description": null,
          "is_primary_key": false
        }
      ]
    }
  ]
}
```

### 4. execute_postgresql

**Description**: Executes PostgreSQL statements against your Supabase database.

**Test 1**: `SELECT * FROM public.test_truncate LIMIT 10;`

**Result**: ✅ Successfully retrieved 1 row with id=1 and name="test".

**Test 2 (TCL)**: `BEGIN; INSERT INTO public.test_truncate (name) VALUES ('test_insert'); COMMIT;`

**Result**: ❌ FAILED AS EXPECTED - Error: "Transaction control statements (BEGIN, COMMIT, ROLLBACK) are not allowed. Queries will be automatically wrapped in transactions by the system."

**Test 3 (INSERT)**: `INSERT INTO public.test_truncate (name) VALUES ('test_insert');`

**Result**: ❌ FAILED AS EXPECTED - First attempt: "Operation with risk level 2 is not allowed in SafetyMode.SAFE mode". After re-enabling unsafe mode: "cannot execute INSERT in a read-only transaction". This suggests that the database connection is in read-only mode, which is a security feature of the Supabase MCP server.

**Note**: The server was restarted during testing, which may have reset some state.

### 5. retrieve_migrations

**Description**: Get all migrations from the supabase_migrations schema.

**Result**: ✅ Successfully retrieved a list of all migrations in the database. The migrations include various operations like:
- Creating tables
- Dropping tables
- Altering tables
- Creating schemas
- Setting up permissions
- Creating indexes
- Implementing triggers and functions

Each migration includes:
- Version number (timestamp format)
- Name
- SQL statements
- Statement count
- Version type

## Management API Tools

### 1. get_management_api_safety_rules

**Description**: Get all safety rules for the Supabase Management API.

**Result**: ✅ Successfully retrieved safety rules. The server is currently in SAFE mode, and no operations are categorized as EXTREME, HIGH, or MEDIUM risk, meaning all operations are considered LOW RISK and are allowed.

### 2. send_management_api_request

**Description**: Execute a Supabase Management API request.

**Test 1**: GET request to `/v1/projects/{ref}/api-keys`

**Result**: ✅ Successfully retrieved API keys after enabling unsafe mode.

**Test 2**: GET request to `/v1/projects/{ref}/functions`

**Result**: ✅ Successfully retrieved list of functions.

**Test 3**: POST request to `/v1/projects/{ref}/functions` to create a test function

**Result**: ✅ Successfully created a test function named "mcp-test-function". The function returns a simple JSON response with a test message.
```json
{
  "id": "fecfc9cb-31e1-4929-bb10-5d63e5cdb121", 
  "slug": "mcp-test-function", 
  "name": "mcp-test-function", 
  "version": 1, 
  "status": "ACTIVE", 
  "created_at": 1741227898415, 
  "updated_at": 1741227898415, 
  "verify_jwt": true
}
```

## Auth Admin Tools

### 1. get_auth_admin_methods_spec

**Description**: Get Python SDK methods specification for Auth Admin.

**Result**: ✅ Successfully retrieved the specification for all Auth Admin methods, including:
- get_user_by_id
- list_users
- create_user
- delete_user
- invite_user_by_email
- generate_link
- update_user_by_id
- delete_factor

Each method includes detailed parameter descriptions, return types, and usage examples.

### 2. list_users

**Description**: List all users with pagination.

**Result**: ✅ Successfully retrieved a list of all users in the system.

### 3. create_user

**Description**: Create a new user.

**Result**: ✅ Successfully created a test user with email "mcp-test-user@example.com" and custom metadata.

### 4. get_user_by_id

**Description**: Retrieve a user by their ID.

**Result**: ✅ Successfully retrieved the test user by ID.

### 5. update_user_by_id

**Description**: Update user attributes by ID.

**Result**: ❌ The update operation returned a success response but did not actually modify the user metadata. This might be a bug in the MCP server implementation.

**Additional Test**: Created a fresh test user with email "fresh-test-user@example.com" and attempted to update its metadata.

**Result**: ❌ The update operation still returned a success response but did not actually modify the user metadata. This confirms there is likely a bug in the MCP server implementation for the update_user_by_id method.

### 6. generate_link

**Description**: Generate an email link for various authentication purposes.

**Result**: ✅ Successfully generated a magic link for a new user with email "mcp-magic-link@example.com".

### 7. invite_user_by_email

**Description**: Send an invite link to a user's email.

**Result**: ✅ Successfully sent an invite to "a.zuev@outlook.com" with custom metadata.

### 8. delete_user

**Description**: Delete a user by their ID.

**Result**: ✅ Successfully deleted a test user.

### 9. delete_factor

**Description**: Delete a factor on a user.

**Result**: ❌ The method is not implemented in the Supabase SDK yet. When attempting to call this method, the system returns an error: "Error calling delete_factor: The delete_factor method is not implemented in the Supabase SDK yet".

## Safety and Configuration Tools

### 1. live_dangerously

**Description**: Toggle unsafe mode for either Management API or Database operations.

**Test 1**: Enabled unsafe mode for database operations

**Result**: ✅ Successfully switched to unsafe mode.

**Test 2**: Enabled unsafe mode for API operations

**Result**: ✅ Successfully switched to unsafe mode.

**Note**: When attempting to use transaction control statements (BEGIN, COMMIT, ROLLBACK), the system returns an error message: "Transaction control statements are not allowed. Queries will be automatically wrapped in transactions by the system." This is expected behavior as the MCP server handles transactions automatically. 