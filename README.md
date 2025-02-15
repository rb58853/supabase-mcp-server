# Supabase MCP Server

An implementation of MCP server for connecting to Supabase PostgreSQL database. Exposes tools to interact with Supabase via MCP protocol.

## Key features
- 💻 Integrates with both Windsurf and Cursor IDEs via `stdio` protocol
- ✅ Supports both local development and production Supabase projects
- 🤑 Rich schema and table metadata for more informative responses
- 🔐 Read-only enforced access to all tables

## Future features
- 🐍 Support every method and object available in native Python SDK 

## To do:
- [ ] Add support for all methods and objects available in native Python SDK
- [ ] Add proper SQL syntax parsing


## Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) - Modern Python package installer
- Local Supabase instance or Supabase project credentials
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official MCP implementation
- PostgreSQL development libraries (required for psycopg2):
  ```bash
  # macOS
  brew install postgresql@16
  
  # Windows
  # Download and install from https://www.postgresql.org/download/windows/

  ```

## Installation

### Setup server
TODO: add installation instructions

### Windsurf

### Cursor
name: supabase
protocol: stdio
command: uvx --directory /Users/az/cursor/supabase-mcp-server run main.py

## Development

1. Clone and setup environment
```bash
git clone https://github.com/alexander-zuev/supabase-mcp-server.git
cd supabase-mcp-server

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install dependencies
```bash
uv sync
```

3. Run the server
```bash
uv run main.py
```

4. Run MCP inspector (for development)
```bash
mcp dev main.py
```
## Local Development
Make sure your local Supabase instance is running:
```bash
supabase start
```

Use the following credentials (defaults for local development):
- Host: `127.0.0.1:54322` (PostgreSQL port)
- Password: `postgres`





