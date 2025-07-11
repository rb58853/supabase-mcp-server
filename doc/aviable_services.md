# Available Services

This section lists the currently available services by name, serving as documentation for completing the [server configuration](../README.md).

## Available Tools

Each tool is identified by the format `ENUM_NAME: name_str`. In the [servers.remote.json](../servers.remote.json) file, you must use the `name_str` value (the one on the right).

### Database Tools

- `GET_SCHEMAS`: get_schemas
- `GET_TABLES`: get_tables
- `GET_TABLE_SCHEMA`: get_table_schema
- `EXECUTE_POSTGRESQL`: execute_postgresql
- `RETRIEVE_MIGRATIONS`: retrieve_migrations

### Safety Tools

- `LIVE_DANGEROUSLY`: live_dangerously
- `CONFIRM_DESTRUCTIVE_OPERATION`: confirm_destructive_operation

### Management API Tools

- `SEND_MANAGEMENT_API_REQUEST`: send_management_api_request
- `GET_MANAGEMENT_API_SPEC`: get_management_api_spec

### Auth Admin Tools

- `GET_AUTH_ADMIN_METHODS_SPEC`: get_auth_admin_methods_spec
- `CALL_AUTH_ADMIN_METHOD`: call_auth_admin_method

### Logs & Analytics Tools

- `RETRIEVE_LOGS`: retrieve_logs

## Resources

This repository does not include default resources.

## Prompts

This repository does not include default prompts.
