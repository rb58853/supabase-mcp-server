# Supabase MCP Server

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/supabase/supabase-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/supabase/supabase-light.svg" />
    <img alt="Supabase" src="assets/supabase/supabase-light.svg" height="40" />
  </picture>
  &nbsp;&nbsp;
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/mcp/mcp-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/mcp/mcp-light.svg" />
    <img alt="MCP" src="assets/mcp/mcp-light.svg" height="40" />
  </picture>
</p>

<p align="center">
  <strong>Supabase MCP server for use with Cursor and Windsurf</strong>
</p>

An implementation of MCP server for connecting to Supabase PostgreSQL database. Exposes tools to interact with Supabase via MCP protocol. Designed for use with Cursor and Windsurf primarily.

## Key features
- 💻 Can be used with both Windsurf and Cursor IDEs via `stdio` protocol
- ✅ Supports both local development and production Supabase projects
- 🤑 Pre-built schema and table queries to help LLMs understand the data + custom query tool to explore data
- 🔐 Read-only access on connection level
- 🔍 Basic SQL syntax validation


## Prerequisites
- Python 3.12+
- PostgreSQL 16+
- uv package manager

### Mac-specific Setup
1. **PostgreSQL Installation (Required for psycopg2)**
   ```bash
   brew install postgresql@16
   ```
   > ⚠️ **Important**: PostgreSQL must be installed BEFORE installing project dependencies. The `psycopg2` package requires PostgreSQL development libraries during compilation.

2. **uv Package Manager**
   ```bash
   pip install uv
   ```

### Windows Setup
1. **PostgreSQL Installation**
   - Download and install PostgreSQL 16+ from https://www.postgresql.org/download/windows/
   - Ensure "PostgreSQL Server" and "Command Line Tools" are selected during installation

2. **uv Package Manager**
   ```bash
   pip install uv
   ```

## Installation

1. Clone and setup environment
```bash
git clone https://github.com/alexander-zuev/supabase-mcp-server.git
cd supabase-mcp-server

# Create and activate virtual environment
uv venv

# Mac/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

2. Install dependencies
```bash
uv sync
```
> 📝 If you get psycopg2 compilation errors, make sure you've installed PostgreSQL first!

## Usage

- **Local development**: MCP server is configured to use local Supabase project by default:
    - Host (project ref): `127.0.0.1:54322` 
    - Password: `postgres`

- **Staging/Production**: MCP server can be configured to connect to any Supabase project:
    ```bash
    export SUPABASE_PROJECT_REF="your-project-ref"  # e.g., "abcdefghijklm"
    export SUPABASE_DB_PASSWORD="your-db-password"
    ```

### Cursor
Add this configuration to Cursor:
```
name: supabase
protocol: stdio
# Local development
command: uv --directory /Users/az/cursor/supabase-mcp-server run main.p # path to the project
# Staging/Production
command: SUPABASE_PROJECT_REF=your-project-ref SUPABASE_DB_PASSWORD=your-db-password uv run main.py
```
Once added, Agent mode will be able to use tools provided by MCP server.



### Windsurf
Windsurf relies on a 'Claude Desktop' like configuration to connect to MCP server. This means you need to edit `mcp_config.json` file to connect to MCP server:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "/Users/az/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/az/cursor/supabase-mcp-server",
        "run",
        "main.py"
      ],
      "env": {
        "SUPABASE_PROJECT_REF": "127.0.0.1:54322", // can be omitted if using local development, required for staging/production
        "SUPABASE_DB_PASSWORD": "postgres" // can be omitted if using local development, required for staging/production
      }
    }
  }
}
```
Once you add this configuration, click refresh and start chatting - Cascade will now be able to use tools provided by MCP server.


## Development

1. Run MCP inspector (for development)
```bash
mcp dev main.py
```

2. Make sure your local Supabase instance is running:
```bash
supabase start
```


## Future improvements
- 🐍 Support methods and objects available in native Python SDK 
- 🔍 Improve SQL syntax validation






