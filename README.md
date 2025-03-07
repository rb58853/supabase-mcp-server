# Supabase MCP Server

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/4a363bcd-7c15-47fa-a72a-d159916517f7" />
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/d255388e-cb1b-42ea-a7b2-0928f031e0df" />
    <img alt="Supabase" src="https://github.com/user-attachments/assets/d255388e-cb1b-42ea-a7b2-0928f031e0df" height="40" />
  </picture>
  &nbsp;&nbsp;
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/38db1bcd-50df-4a49-a106-1b5afd924cb2" />
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/82603097-07c9-42bb-9cbc-fb8f03560926" />
    <img alt="MCP" src="https://github.com/user-attachments/assets/82603097-07c9-42bb-9cbc-fb8f03560926" height="40" />
  </picture>
</p>

<p align="center">
  <strong>Let Cursor & Windsurf manage your Supabase and run SQL queries. Autonomously. In a safe way.</strong>
</p>

[![Star History Chart](https://api.star-history.com/svg?repos=alexander-zuev/supabase-mcp-server&type=Date)](https://star-history.com/#alexander-zuev/supabase-mcp-server&Date)

<p align="center">
  <a href="https://pypi.org/project/supabase-mcp-server/"><img src="https://img.shields.io/pypi/v/supabase-mcp-server.svg" alt="PyPI version" /></a>
  <a href="https://github.com/alexander-zuev/supabase-mcp-server/actions"><img src="https://github.com/alexander-zuev/supabase-mcp-server/workflows/CI/badge.svg" alt="CI Status" /></a>
  <a href="https://codecov.io/gh/alexander-zuev/supabase-mcp-server"><img src="https://codecov.io/gh/alexander-zuev/supabase-mcp-server/branch/main/graph/badge.svg" alt="Code Coverage" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg" alt="Python 3.12+" /></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/uv-package%20manager-blueviolet" alt="uv package manager" /></a>
  <a href="https://pepy.tech/project/supabase-mcp-server"><img src="https://static.pepy.tech/badge/supabase-mcp-server" alt="PyPI Downloads" /></a>
  <a href="https://smithery.ai/badge/@alexander-zuev/supabase-mcp-server"><img src="https://smithery.ai/badge/@alexander-zuev/supabase-mcp-server" alt="Smithery.ai Downloads" /></a>
  <a href="https://modelcontextprotocol.io/introduction"><img src="https://img.shields.io/badge/MCP-Server-orange" alt="MCP Server" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License" /></a>
</p>

A feature-rich MCP server that enables Cursor and Windsurf to safely interact with Supabase databases. It provides tools for database management, SQL query execution, and Supabase Management API access with built-in safety controls.

## Table of contents
<p align="center">
  <a href="#getting-started">Getting started</a> •
  <a href="#feature-overview">Feature overview</a> •
  <a href="#troubleshooting">Troubleshooting</a> •
  <a href="#roadmap">Roadmap</a>
</p>

## ✨ Key features
- 💻 Compatible with Cursor, Windsurf, Cline and other MCP clients supporting `stdio` protocol
- 🔐 Control read-only and read-write modes of SQL query execution
- 🔍 Runtime SQL query validation with risk level assessment
- 🛡️ Three-tier safety system for SQL operations: safe, write, and destructive
- 🔄 Robust transaction handling for both direct and pooled database connections
- 📝 Automatic versioning of database schema changes
- 💻 Manage your Supabase projects with Supabase Management API
- 🧑‍💻 Manage users with Supabase Auth Admin methods via Python SDK
- 🔨 Pre-built tools to help Cursor & Windsurf work with MCP more effectively
- 📦 Dead-simple install & setup via package manager (uv, pipx, etc.)


## Getting Started

### Prerequisites
Installing the server requires the following on your system:
- Python 3.12+

If you plan to install via `uv`, ensure it's [installed](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1).

### PostgreSQL Installation
PostgreSQL installation is no longer required for the MCP server itself, as it now uses asyncpg which doesn't depend on PostgreSQL development libraries.

However, you'll still need PostgreSQL if you're running a local Supabase instance:

**MacOS**
```bash
brew install postgresql@16
```

**Windows**
  - Download and install PostgreSQL 16+ from https://www.postgresql.org/download/windows/
  - Ensure "PostgreSQL Server" and "Command Line Tools" are selected during installation

### Step 1. MCP Server Installation

Since v0.2.0 I introduced support for package installation. You can use your favorite Python package manager to install the server via:

```bash
# if pipx is installed (recommended)
pipx install supabase-mcp-server

# if uv is installed
uv pip install supabase-mcp-server
```

`pipx` is recommended because it creates isolated environments for each package.

You can also install the server manually by cloning the repository and running `pipx install -e .` from the root directory.

#### Installing from source
If you would like to install from source, for example for local development:
```bash
uv venv
# On Mac
source .venv/bin/activate
# On Windows
.venv\Scripts\activate
# Install package in editable mode
uv pip install -e .
```

#### Installing via Smithery.ai
Please report any issues with Smithery, as I haven't tested it yet.

To install Supabase MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@alexander-zuev/supabase-mcp):

```bash
npx -y @smithery/cli install @alexander-zuev/supabase-mcp --client claude
```

### Step 2. Configuration

After installing the package, you'll need to configure your database connection settings. The server supports both local and remote Supabase instances.

#### Local Supabase instance (Default)
Server is pre-configured to connect to the local Supabase instance using default settings:
- `Host`: 127.0.0.1:54322
- `Password`: postgres
- `API URL`: http://127.0.0.1:54321

>💡 As long as you didn't modify the default settings and you want to connect to the local instance, you don't need to set environment variables.

#### Remote Supabase instance

> ⚠️ **IMPORTANT WARNING**: Session pooling connections are not supported and there are no plans to support it yet. Let me know if you feel there is a use case for supporting this in an MCP server

For remote Supabase projects, you need to configure:
- `SUPABASE_PROJECT_REF` - Your project reference (found in project URL)
- `SUPABASE_DB_PASSWORD` - Your database password
- `SUPABASE_REGION` - (Optional) Defaults to `us-east-1`
- `SUPABASE_ACCESS_TOKEN` - (Optional) For Management API access
- `SUPABASE_SERVICE_ROLE_KEY` - (Optional) For Auth Admin SDK access

You can get your SUPABASE_PROJECT_REF from your project's dashboard URL:
- `https://supabase.com/dashboard/project/<supabase-project-ref>`

The server supports all Supabase regions:
- `us-west-1` - West US (North California)
- `us-east-1` - East US (North Virginia) - default
- `us-east-2` - East US (Ohio)
- `ca-central-1` - Canada (Central)
- `eu-west-1` - West EU (Ireland)
- `eu-west-2` - West Europe (London)
- `eu-west-3` - West EU (Paris)
- `eu-central-1` - Central EU (Frankfurt)
- `eu-central-2` - Central Europe (Zurich)
- `eu-north-1` - North EU (Stockholm)
- `ap-south-1` - South Asia (Mumbai)
- `ap-southeast-1` - Southeast Asia (Singapore)
- `ap-northeast-1` - Northeast Asia (Tokyo)
- `ap-northeast-2` - Northeast Asia (Seoul)
- `ap-southeast-2` - Oceania (Sydney)
- `sa-east-1` - South America (São Paulo)

#### Configuration Methods

The server looks for configuration in this order:
1. Environment variables (highest priority)
2. Local `.env` file in current directory
3. Global config file:
   - Windows: `%APPDATA%/supabase-mcp/.env`
   - macOS/Linux: `~/.config/supabase-mcp/.env`
4. Default settings (local development)

##### Cursor
Since Cursor v0.46 there are two ways to configure MCP servers:
- per project basis -> create `mcp.json` in your project / repo folder and `.env` to configure connection
- globally -> create an MCP server in Settings and configure using `.env` which is supported by this MCP server only

You can create project-specific MCP by:
- creating .cursor folder in your repo, if doesn't exist
- creating or updating `mcp.json` file with the following settings

> ⚠ **Environment variables**: If you are configuring MCP server on a per-project basis you still need to create .env file for connection settings to be picked up. I wasn't able to configure mcp.json to pick up my env vars 😔

```json
{
	"mcpServers": {
	  "supabase": {
		"command": "supabase-mcp-server"
	  }
	}
}
```

Alternatively, if you want to configure MCP servers globally (i.e. not for each project), you can use configure connection settings by updating an `.env` file in a global config folder by running the following commands:
```bash
# Create config directory and navigate to it
# On macOS/Linux
mkdir -p ~/.config/supabase-mcp
cd ~/.config/supabase-mcp

# On Windows (in PowerShell)
mkdir -Force "$env:APPDATA\supabase-mcp"
cd "$env:APPDATA\supabase-mcp"
```
This creates the necessary config folder where your environment file will be stored.

```bash
# Create and edit .env file
# On macOS/Linux
nano ~/.config/supabase-mcp/.env

# On Windows (PowerShell)
notepad "$env:APPDATA\supabase-mcp\.env"
```

This will open the .env file. Once the file is open, copy & paste the following:
```bash
SUPABASE_PROJECT_REF=your-project-ref
SUPABASE_DB_PASSWORD=your-db-password
SUPABASE_REGION=us-east-1  # optional, defaults to us-east-1
SUPABASE_ACCESS_TOKEN=your-access-token  # optional, for management API
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key # optional, for Auth Admin SDK
```

Verify the file exists - you should see the values you have just set:
```bash
# On macOS/Linux
cat ~/.config/supabase-mcp/.env

# On Windows (PowerShell)
Get-Content "$env:APPDATA\supabase-mcp\.env"
```

You can find global config file:
   - Windows: `%APPDATA%/supabase-mcp/.env`
   - macOS/Linux: `~/.config/supabase-mcp/.env`


##### Windsurf
Windsurf supports de facto standard .json format for MCP Servers configuration. You can configure the server in mcp_config.json file:
```json
{
    "mcpServers": {
      "supabase": {
        "command": "/Users/username/.local/bin/supabase-mcp-server",  // update path
        "env": {
          "SUPABASE_PROJECT_REF": "your-project-ref",
          "SUPABASE_DB_PASSWORD": "your-db-password",
          "SUPABASE_REGION": "us-east-1",  // optional, defaults to us-east-1
          "SUPABASE_ACCESS_TOKEN": "your-access-token",  // optional, for management API
          "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key"  // optional, for Auth Admin SDK
        }
      }
    }
}
```
> 💡 **Finding the server path**:
> - macOS/Linux: Run `which supabase-mcp-server`
> - Windows: Run `where supabase-mcp-server`

#### Configuration Precedence
The server looks for configuration in this order:
1. Environment variables (highest priority)
2. Local `.env` file in current directory
3. Global config file:
   - Windows: `%APPDATA%/supabase-mcp/.env`
   - macOS/Linux: `~/.config/supabase-mcp/.env`
4. Default settings (local development)

### Step 3. Running MCP Server in Cursor/Windsurf

In general, any MCP client that supports `stdio` protocol should work with this MCP server (Cline, for example) but I haven't tested it with anything except Cursor/Windsurf.

#### Cursor
Go to Settings -> Features -> MCP Servers and add a new server with this configuration:
```bash
# can be set to any name
name: supabase
type: command
# if you installed with pipx
command: supabase-mcp-server
# if you installed with uv
command: uv run supabase-mcp-server
# if the above doesn't work, use the full path (recommended)
command: /full/path/to/supabase-mcp-server  # Find with 'which supabase-mcp-server' (macOS/Linux) or 'where supabase-mcp-server' (Windows)
```

If configuration is correct, you should see a green dot indicator and the number of tools exposed by the server.
![How successful Cursor config looks like](https://github.com/user-attachments/assets/45df080a-8199-4aca-b59c-a84dc7fe2c09)

#### Windsurf
Go to Cascade -> Click on the hammer icon -> Configure -> Fill in the configuration:
```json
{
    "mcpServers": {
      "supabase": {
        "command": "/Users/username/.local/bin/supabase-mcp-server",  // update path
        "env": {
          "SUPABASE_PROJECT_REF": "your-project-ref",
          "SUPABASE_DB_PASSWORD": "your-db-password",
          "SUPABASE_REGION": "us-east-1",  // optional, defaults to us-east-1
          "SUPABASE_ACCESS_TOKEN": "your-access-token",  // optional, for management API
          "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key"  // optional, for Auth Admin SDK
        }
      }
    }
}
```
If configuration is correct, you should see green dot indicator and clickable supabase server in the list of available servers.

![How successful Windsurf config looks like](https://github.com/user-attachments/assets/322b7423-8c71-410b-bcab-aff1b143faa4)

### Troubleshooting

Here are some tips & tricks that might help you:
- **Debug installation** - run `supabase-mcp-server` directly from the terminal to see if it works. If it doesn't, there might be an issue with the installation.
- **MCP Server configuration** - if the above step works, it means the server is installed and configured correctly. As long as you provided the right command, IDE should be able to connect. Make sure to provide the right path to the server executable.
- **"No tools found" error** - If you see "Client closed - no tools available" in Cursor despite the package being installed:
  - Find the full path to the executable by running `which supabase-mcp-server` (macOS/Linux) or `where supabase-mcp-server` (Windows)
  - Use the full path in your MCP server configuration instead of just `supabase-mcp-server`
  - For example: `/Users/username/.local/bin/supabase-mcp-server` or `C:\Users\username\.local\bin\supabase-mcp-server.exe`
- **Environment variables** - to connect to the right database, make sure you either set env variables in `mcp_config.json` or in `.env` file placed in a global config directory (`~/.config/supabase-mcp/.env` on macOS/Linux or `%APPDATA%\supabase-mcp\.env` on Windows).
- **Accessing logs** - The MCP server writes detailed logs to a file:
  - Log file location:
    - macOS/Linux: `~/.local/share/supabase-mcp/mcp_server.log`
    - Windows: `%USERPROFILE%\.local\share\supabase-mcp\mcp_server.log`
  - Logs include connection status, configuration details, and operation results
  - View logs using any text editor or terminal commands:
    ```bash
    # On macOS/Linux
    cat ~/.local/share/supabase-mcp/mcp_server.log

    # On Windows (PowerShell)
    Get-Content "$env:USERPROFILE\.local\share\supabase-mcp\mcp_server.log"
    ```

If you are stuck or any of the instructions above are incorrect, please raise an issue.

### MCP Inspector
A super useful tool to help debug MCP server issues is MCP Inspector. If you installed from source, you can run `supabase-mcp-inspector` from the project repo and it will run the inspector instance. Coupled with logs this will give you complete overview over what's happening in the server.
> 📝 Running `supabase-mcp-inspector`, if installed from package, doesn't work properly - I will validate and fix in the coming release.

## Feature Overview

### Database query tools

Since v0.3+ server provides comprehensive database management capabilities with built-in safety controls:

- **SQL Query Execution**: Execute any PostgreSQL query with intelligent risk assessment
  - **Three-tier safety system**:
    - `safe`: Read-only operations (SELECT, EXPLAIN) - always allowed
    - `write`: Data modification operations (INSERT, UPDATE, DELETE) - require unsafe mode
    - `destructive`: Schema-changing operations (DROP, TRUNCATE) - require unsafe mode and confirmation

- **SQL Parsing and Validation**:
  - Uses PostgreSQL's own parser (via pglast) for accurate query analysis
  - Precisely identifies query types and potential risks
  - Validates syntax before execution to prevent errors
  - Categorizes statements into DQL, DML, DDL, DCL, and TCL types
  - Provides detailed feedback on query safety and required permissions

- **Automatic Migration Versioning**:
  - All schema-changing operations (DDL) are automatically versioned
  - Creates timestamped migration entries in Supabase's migration system
  - Generates descriptive migration names based on operation type and target
  - Includes CREATE, ALTER, DROP, GRANT, REVOKE operations
  - Maintains a complete history of schema changes for better tracking and rollback capabilities

- **Safety Controls**:
  - All database tools start in SAFE mode by default (only read-only operations are allowed)
  - All statements are executed in transaction mode by the `asyncpg` client
  - 2-step confirmation is required for high-risk / destructive operations

- **Available Tools**:
  - `get_schemas`: Lists all database schemas with their sizes and table counts
  - `get_tables`: Lists tables, foreign tables, and views in a schema with metadata
  - `get_table_schema`: Gets detailed table structure including columns, keys, and relationships
  - `execute_postgresql`: Executes PostgreSQL statements against your Supabase database
  - `confirm_destructive_operation`: Executes high-risk operations after explicit confirmation
  - `retrieve_migrations`: Gets all migrations from the supabase_migrations schema
  - `live_dangerously`: Toggles between safe and unsafe operation modes

### Management API tools

Since v0.3.0 server provides secure access to the Supabase Management API with built-in safety controls:

- **Available Tools**:
  - `send_management_api_request`: Sends arbitrary requests to Supabase Management API with auto-injection of project ref
  - `get_management_api_spec`: Gets the enriched API specification with safety information
    - Supports multiple query modes: by domain, by specific path/method, or all paths
    - Includes risk assessment information for each endpoint
    - Provides detailed parameter requirements and response formats
    - Helps LLMs understand the full capabilities of the Supabase Management API
  - `get_management_api_safety_rules`: Gets all safety rules with human-readable explanations
  - `live_dangerously`: Toggles between safe and unsafe operation modes

- **Safety Controls**:
  - Uses the same safety manager as database operations for consistent risk management
  - Operations categorized by risk level:
    - `safe`: Read-only operations (GET) - always allowed
    - `unsafe`: State-changing operations (POST, PUT, PATCH, DELETE) - require unsafe mode
    - `blocked`: Destructive operations (delete project, etc.) - never allowed
  - Default safe mode prevents accidental state changes
  - Path-based pattern matching for precise safety rules

**Note**: Management API tools only work with remote Supabase instances and are not compatible with local Supabase development setups.

### Auth Admin tools

I was planning to add support for Python SDK methods to the MCP server. Upon consideration I decided to only add support for Auth admin methods as I often found myself manually creating test users which was prone to errors and time consuming. Now I can just ask Cursor to create a test user and it will be done seamlessly. Check out the full Auth Admin SDK method docs to know what it can do.

Since v0.3.6 server supports direct access to Supabase Auth Admin methods via Python SDK:
  - Includes the following tools:
    - `get_auth_admin_methods_spec` to retrieve documentation for all available Auth Admin methods
    - `call_auth_admin_method` to directly invoke Auth Admin methods with proper parameter handling
  - Supported methods:
    - `get_user_by_id`: Retrieve a user by their ID
    - `list_users`: List all users with pagination
    - `create_user`: Create a new user
    - `delete_user`: Delete a user by their ID
    - `invite_user_by_email`: Send an invite link to a user's email
    - `generate_link`: Generate an email link for various authentication purposes
    - `update_user_by_id`: Update user attributes by ID
    - `delete_factor`: Delete a factor on a user (currently not implemented in SDK)

#### Why use Auth Admin SDK instead of raw SQL queries?

The Auth Admin SDK provides several key advantages over direct SQL manipulation:
- **Functionality**: Enables operations not possible with SQL alone (invites, magic links, MFA)
- **Accuracy**: More reliable then creating and executing raw SQL queries on auth schemas
- **Simplicity**: Offers clear methods with proper validation and error handling

  - Response format:
    - All methods return structured Python objects instead of raw dictionaries
    - Object attributes can be accessed using dot notation (e.g., `user.id` instead of `user["id"]`)
  - Edge cases and limitations:
    - UUID validation: Many methods require valid UUID format for user IDs and will return specific validation errors
    - Email configuration: Methods like `invite_user_by_email` and `generate_link` require email sending to be configured in your Supabase project
    - Link types: When generating links, different link types have different requirements:
      - `signup` links don't require the user to exist
      - `magiclink` and `recovery` links require the user to already exist in the system
    - Error handling: The server provides detailed error messages from the Supabase API, which may differ from the dashboard interface
    - Method availability: Some methods like `delete_factor` are exposed in the API but not fully implemented in the SDK

### Automatic Versioning of Database Changes

"With great power comes great responsibility." While `execute_postgresql` tool coupled with aptly named `live_dangerously` tool provide a powerful and simple way to manage your Supabase database, it also means that dropping a table or modifying one is one chat message away. In order to reduce the risk of irreversible changes, since v0.3.8 the server supports:
- automatic creation of migration scripts for all write & destructive sql operations executed on the database
- improved safety mode of query execution, in which all queries are categorized in:
  - `safe` type: always allowed. Includes all read-only ops.
  - `write`type: requires `write` mode to be enabled by the user.
  - `destructive` type: requires `write` mode to be enabled by the user AND a 2-step confirmation of query execution for clients that do not execute tools automatically.

### Universal Safety Mode
Since v0.3.8 Safety Mode has been standardized across all services (database, API, SDK) using a universal safety manager. This provides consistent risk management and a unified interface for controlling safety settings across the entire MCP server.

All operations (SQL queries, API requests, SDK methods) are categorized into risk levels:
- `Low` risk: Read-only operations that don't modify data or structure (SELECT queries, GET API requests)
- `Medium` risk: Write operations that modify data but not structure (INSERT/UPDATE/DELETE, most POST/PUT API requests)
- `High` risk: Destructive operations that modify database structure or could cause data loss (DROP/TRUNCATE, DELETE API endpoints)
- `Extreme` risk: Operations with severe consequences that are blocked entirely (deleting projects)

Safety controls are applied based on risk level:
- Low risk operations are always allowed
- Medium risk operations require unsafe mode to be enabled
- High risk operations require unsafe mode AND explicit confirmation
- Extreme risk operations are never allowed

This universal approach ensures consistent protection across all server components while providing flexibility for legitimate operations when needed.

## Feature Changelog

- 📦 Simplified installation via package manager - ✅ (v0.2.0)
- 🌎 Support for different Supabase regions - ✅ (v0.2.2)
- 🎮 Programmatic access to Supabase management API with safety controls - ✅ (v0.3.0)
- 👷‍♂️ Read and read-write database SQL queries with safety controls - ✅ (v0.3.0)
- 🔄 Robust transaction handling for both direct and pooled connections - ✅ (v0.3.2)
- 🐍 Support methods and objects available in native Python SDK - ✅ (v0.3.6)
- 🔍 Stronger SQL query validation ✅ (v0.3.8)
- 📝 Automatic versioning of database changes ✅ (v0.3.8)
- 📖 Radically improved knowledge and tools of api spec ✅ (v0.3.8)
- 🪵 Tools / resources to more easily access database, edge functions logs (?)


For a more detailed roadmap, please see this [discussion](github.com) on GitHub.

### Connect to Supabase logs

I'm planning to research, if it's possible to connect to Supabase db logs which might be useful for debugging (if not already supported.)


---

Enjoy! ☺️
