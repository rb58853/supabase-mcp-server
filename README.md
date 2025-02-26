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
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg" alt="Python 3.12+" /></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/uv-package%20manager-blueviolet" alt="uv package manager" /></a>
  <a href="https://smithery.ai/server/@alexander-zuev/supabase-mcp"><img src="https://smithery.ai/badge/@alexander-zuev/supabase-mcp" alt="smithery badge" /></a>
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
- 🔄 Robust transaction handling for both direct and pooled database connections
- 💻 Manage your Supabase projects with Supabase Management API
- 🔨 Pre-built tools to help Cursor & Windsurf work with MCP more effectively
- 📦 Dead-simple install & setup via package manager (uv, pipx, etc.)

## Getting Started

### Prerequisites
Installing the server requires the following on your system:
- Python 3.12+
- PostgresSQL 16+

If you plan to install via `uv`, ensure it's [installed](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_1).

### PostgreSQL Installation
> ⚠️ **Important**: PostgreSQL must be installed BEFORE installing project dependencies, as psycopg2 requires PostgreSQL development libraries during compilation.

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

You can also install the server manually by cloning the repository and running `pipx` install -editable . from the root directory.

> ⚠️ If you run into psycopg2 compilation issues, you might be missing PostgreSQL development packages. See above.

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

>💡 As long as you didn't modify the default settings and you want to connect to the local instance, you don't need to set environment variables.

#### Remote Supabase instance

> ⚠️ **IMPORTANT WARNING**: Session pooling connections are NOT supported yet. Use  transaction pooling and direct connections instead. I'm planning to add / modify connection to support this in v0.4 (soon).

![Session pool connections are not supported yet](https://github.com/user-attachments/assets/c01e0e06-8fdc-4632-bde5-922c7a527897)

For remote Supabase projects, you need to configure:
- `SUPABASE_PROJECT_REF` - Your project reference (found in project URL)
- `SUPABASE_DB_PASSWORD` - Your database password
- `SUPABASE_REGION` - (Optional) Defaults to `us-east-1`
- `SUPABASE_ACCESS_TOKEN` - (Optional) For Management API access

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

Method of MCP configuration differs between Cursor and Windsurf. Read the relevant section to understand how to configure connection.

##### Cursor
Since v0.46 there are two ways to configure MCP servers in Cursor:
- per project basis -> create `mcp.json` in your project / repo folder and `.env` to configure connection
- globally -> create an MCP server in Settings and configure using `.env` which is supported by this MCP server only


You can create project-specific MCP by:
- creating .cursor folder in your repo, if doesn't exist
- creating or updating `mcp.json` file with the following settings

> ⚠ **Environment variables**: If you are configuring MCP server on a per-project basis you still need to create .env file for connection settings to be picked up. I wasn't able to configure mcp.json to pick up my env vars 😔

```json
{
	"mcpServers": {
	  "filesystem": {
		"command": "supabase-mcp-server",
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
          "SUPABASE_ACCESS_TOKEN": "your-access-token"  // optional, for management API
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
          "SUPABASE_ACCESS_TOKEN": "your-access-token"  // optional, for management API
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

If you are stuck or any of the instructions above are incorrect, please raise an issue on GitHub.

### MCP Inspector
A super useful to

## Feature Overview

### Database query tools

Since v0.3.0 server supports both read-only and data modification operations:

- **Read operations**: SELECT queries for data retrieval
- **Data Manipulation Language (DML)**: INSERT, UPDATE, DELETE operations for data changes
- **Data Definition Language (DDL)**: CREATE, ALTER, DROP operations for schema changes*

*Note: DDL operations require:
1. Read-write mode enabled via `live_dangerously`
2. Sufficient permissions for the connected database role

#### Transaction Handling

The server supports two approaches for executing write operations:

1. **Explicit Transaction Control** (Recommended):
   ```sql
   BEGIN;
   CREATE TABLE public.test_table (id SERIAL PRIMARY KEY, name TEXT);
   COMMIT;
   ```

2. **Single Statements**:
   ```sql
   CREATE TABLE public.test_table (id SERIAL PRIMARY KEY, name TEXT);
   ```

For DDL operations (CREATE/ALTER/DROP), we strongly recommend using explicit transaction control with BEGIN/COMMIT blocks for better reliability and control.

#### Connection Types

The server works with both:
- **Direct Database Connections**: Full transaction control, supports all operations
- **Transaction Pooler Connections**: Used by default in Supabase production/staging environments

> ⚠️ **IMPORTANT WARNING**: Session pooling connections are NOT SUPPORTED. Use  transaction pooling and direct connections instead. I'm planning to add / modify connection to support this in v0.4 (soon).

When connecting via Supabase's Transaction Pooler, some complex transaction patterns may not work as expected. For schema changes in these environments, use explicit transaction blocks or consider using Supabase migrations or the SQL Editor in the dashboard.

Available database tools:
- `get_db_schemas` - Lists all database schemas with their sizes and table counts
- `get_tables` - Lists all tables in a schema with their sizes, row counts, and metadata
- `get_table_schema` - Gets detailed table structure including columns, keys, and relationships
- `execute_sql_query` - Executes raw SQL queries with comprehensive support for all PostgreSQL operations:
  - Supports all query types (SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, etc.)
  - Handles transaction control statements (BEGIN, COMMIT, ROLLBACK)


- Supported modes:
  - `read-only` - only read-only queries are allowed (default mode)
  - `read-write` - all SQL operations are allowed when explicitly enabled
- Safety features:
  - Starts in read-only mode by default
  - Requires explicit mode switch for write operations
  - Automatically resets to read-only mode after write operations
  - Intelligent transaction state detection to prevent errors
  - SQL query validation [TODO]

### Management API tools
Since v0.3.0 server supports sending arbitrary requests to Supabase Management API with auto-injection of project ref and safety mode control:
  - Includes the following tools:
    - `send_management_api_request` to send arbitrary requests to Supabase Management API, with auto-injection of project ref and safety mode control
    - `get_management_api_spec` to get the enriched API specification with safety information
    - `get_management_api_safety_rules` to get all safety rules including blocked and unsafe operations with human-readable explanations
    - `live_dangerously` to switch between safe and unsafe modes
  - Safety features:
    - Divides API methods into `safe`, `unsafe` and `blocked` categories based on the risk of the operation
    - Allows to switch between safe and unsafe modes dynamically
    - Blocked operations (delete project, delete database) are not allowed regardless of the mode


## Roadmap

- 📦 Simplified installation via package manager - ✅ (v0.2.0)
- 🌎 Support for different Supabase regions - ✅ (v0.2.2)
- 🎮 Programmatic access to Supabase management API with safety controls - ✅ (v0.3.0)
- 👷‍♂️ Read and read-write database SQL queries with safety controls - ✅ (v0.3.0)
- 🔄 Robust transaction handling for both direct and pooled connections - ✅ (v0.3.2)
- 👨‍💻 Supabase CLI integration? (if necessary)
- 🐍 Support methods and objects available in native Python SDK
- 🔍 Strong SQL query validation
- 📝 Connect to db logs to help debug errors (Pull in [edge functions logs](https://supabase.com/dashboard/project/drmzszdytvvfbcytltsw/logs/edge-logs))
- ⚓️ Simplify connection via a string?

### Support of Python SDK methods

I'm planning to add support for Auth methods from Python SDK as it would allow Cursor to create test users for me, which might be handy.

### Connect to Supabase logs

I'm planning to research, if it's possible to connect to Supabase db logs which might be useful for debugging (if not already supported.)


---

Enjoy! ☺️
