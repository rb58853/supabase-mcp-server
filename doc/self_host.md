# Supabase on Docker Host (VPS Use Case)

Supabase can be deployed not only locally or on the official Supabase cloud, but also via Docker using the [docker-compose.yml](https://github.com/supabase/supabase/tree/master/docker) file provided by Supabase. This approach is commonly used for deploying Supabase on a VPS or any Docker-compatible environment. For such deployments, some adjustments to the `.env` file are necessary. The following environment variables must be added:

```env
# Docker Container Environment
CONTAINER_EXPOSE_IP=<your-vps-ip> #default: 127.0.0.1

## DATABASE
DATABASE_NAME=postgres
DATABASE_USER=postgres

## POOLER
POOLER_PROXY_PORT_TRANSACTION=6543
POOLER_TENANT_ID=your-tenant-id
```

The IP address of your host (either VPS or localhost) should be known to the person deploying the application. The other variables (`DATABASE_NAME`, `DATABASE_USER`, `POOLER_PROXY_PORT_TRANSACTION`, `POOLER_TENANT_ID`) can be found in your docker-compose file or in the environment variables of your Supabase Docker instance. See an [example here](https://github.com/supabase/supabase/blob/master/docker/docker-compose.yml).

Additionally, the `SUPABASE_PROJECT_REF` variable must contain the exact address of your hosted instance, such as: `https://supabas.mydns.dev` or `https://123.45.67.89:8000`.

## Connection Code Example

Each new environment variable serves a specific purpose, as illustrated in the following example, which builds a connection URL for the database. It is important to use only the plain IP of your Docker instance, without including the port or the `https://` prefix.

```python
def _build_connection_string(self) -> str:
    """Build the database connection string for asyncpg.
    Returns:
        PostgreSQL connection string compatible with asyncpg
    """
    encoded_password = urllib.parse.quote_plus(self.db_password)

    if self.project_ref.startswith("http://") or self.project_ref.startswith("https://"):
        # Docker development
        DATABASE_PASSWORD = self._settings.supabase_db_password
        DATABASE_USER = self._settings.database_user
        CONTAINER_EXPOSE_IP = self._settings.CONTAINER_EXPOSE_IP
        POOLER_PROXY_PORT_TRANSACTION = self._settings.pooler_proxy_port_transaction
        POOLER_TENANT_ID = self._settings.pooler_tenant_id
        DATABASE_NAME = self._settings.database_name

        connection_string = f"postgresql://{DATABASE_NAME}.{POOLER_TENANT_ID}:{DATABASE_PASSWORD}@{CONTAINER_EXPOSE_IP}:{POOLER_PROXY_PORT_TRANSACTION}/{DATABASE_USER}"

        return connection_string
    ...    
```

## Testing the Docker Connection

To verify that your Docker instance connection works correctly, you can use the simple example provided in [this repository](https://github.com/rb58853/supabase-connection-tester). This allows you to ensure the connection is established before integrating it into a larger and more complex project environment. It is recommended to copy the `.env` file you are using in your main project and run the suggested repository with the same environment variables.

```shell
# Exit the root directory of this project (supabase-mcp) if inside
cd ..

# Clone the repository locally
git clone https://github.com/rb58853/supabase-connection-tester.git

# Copy the same environment variables
```

It is advisable to consult the documentation of the cloned repository if you intend to use it. See [here](https://github.com/rb58853/supabase-connection-tester).
