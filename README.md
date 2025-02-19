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
  <strong>Let Cursor & Windsurf interact with Supabase</strong>
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



Unofficial Supabase MCP server that enables Cursor and Windsurf to interact directly with Supabase PostgreSQL database. Pre-configured to work with local and production instances.

## ✨ Key features
- 💻 Designed to work with Windsurf, Cursor, Cline and other MCP-compatible IDEs
- ✅ Pre-configured to work with both free and paid Supabase projects (direct and transaction pooling connection)
- 🔨 Pre-built database exploration tools with schema insights greatly improve LLM 'onboarding experience' into your db
- 🔐 Enforces read-only mode when executing SQL queries
- 🔍 Basic QoL features like query validation, retry logic for connection errors
- 📦 Installation via package manager (uv, pipx, etc.) or from source

## Prerequisites
- Python 3.12+
- PostgreSQL 16+
- uv package manager

### PostgreSQL Installation
> ⚠️ **Important**: PostgreSQL must be installed BEFORE installing project dependencies, as psycopg2 requires PostgreSQL development libraries during compilation.

**MacOS**
```bash
brew install postgresql@16
```

**Windows**
  - Download and install PostgreSQL 16+ from https://www.postgresql.org/download/windows/
  - Ensure "PostgreSQL Server" and "Command Line Tools" are selected during installation

## MCP Server Installation

> ⚠️  **0.2.0 Breaking change**: Installation and execution methods have changed to support package distribution. The server now runs as a proper Python module instead of a direct script.

You can install Supabase MCP Server either using a package manager (recommended) or from source (just as in v0.1.0).

### Using Package Managers (Recommended)

Choose the installation method based on your needs:

```bash
# Using pipx (recommended for CLI tools)
pipx install supabase-mcp-server
# → Run with: supabase-mcp-server

# Using UV (if you prefer your current environment)
uv pip install supabase-mcp-server
# → Run with: uv run supabase-mcp-server
```

Why these package managers?
- `pipx`:
  - Creates isolated environments for CLI tools
  - Makes commands globally available as `supabase-mcp-server`
  - Prevents dependency conflicts
  - Best for end users who just want to use the tool

- `uv`:
  - Installs in your current environment
  - Faster installation and dependency resolution
  - Requires `uv run` prefix to execute
  - Better for development or if you're using uv for other packages

### Installing from Source

1. Clone the repository
```bash
git clone https://github.com/alexander-zuev/supabase-mcp-server.git
cd supabase-mcp-server
```

2. Create and activate virtual environment
```bash
# Create venv
uv venv

# Activate it
# On Mac/Linux
source .venv/bin/activate
# On Windows
.venv\Scripts\activate
```

3. Install in editable mode
```bash
uv pip install -e .
```

### Installing via Smithery

Please report any issues with Smithery, as I haven't tested it yet.

To install Supabase MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@alexander-zuev/supabase-mcp):

```bash
npx -y @smithery/cli install @alexander-zuev/supabase-mcp --client claude
```


## Running Supabase MCP Server

This MCP server was designed to be used with AI IDEs like Cursor and Windsurf and not tested with other clients. However, it should work with any MCP-compatible IDE as long as it uses stdio protocol.

You can run the server in several ways:
- as a package script (if you installed it using package manager)
- as a python module (if you installed it from source)

> 💡 **0.2.0 Breaking change**: Installation and execution methods have changed to support package distribution. The server now runs as a proper Python module instead of a direct script:
> - Old: `uv --directory /path/to/supabase-mcp-server run main.py`
> - New: `uv run supabase-mcp-server` (if installed via package manager)
> - New: `uv --directory /path/to/supabase-mcp-server run python -m supabase_mcp.main` (if installed from source)


### Running as a package script (if you installed it using package manager)

If you installed it using package manager, you can run the server with this command:

```bash
# Pipx
supabase-mcp-server

# UV
uv run supabase-mcp-server
```


#### Setup Cursor

> ⚠️ **Important**: Unlike Windsurf's defacto standard JSON configuration, Cursor team had a 'genius' idea to abstract away the underlying configuration into a barebones, poorly documented UI (took me several hours to figure out how to set it up) 😡. So in order to connect to a remote Supabase project, you need to set environment variables globally. I've provided a way to pick up .env file from a global config directory (`~/.config/supabase-mcp/.env` on macOS/Linux or `%APPDATA%\supabase-mcp\.env` on Windows).

1. Set up global config (recommended approach):
```bash
# Create config directory
# On macOS/Linux
mkdir -p ~/.config/supabase-mcp && cd ~/.config/supabase-mcp
# On Windows (in PowerShell)
mkdir -Force "$env:APPDATA\supabase-mcp" ; cd "$env:APPDATA\supabase-mcp"

# Create and open .env file
# On macOS/Linux
echo "SUPABASE_PROJECT_REF=your-project-ref
SUPABASE_DB_PASSWORD=your-db-password" > .env && open .
# On Windows (in PowerShell)
echo "SUPABASE_PROJECT_REF=your-project-ref
SUPABASE_DB_PASSWORD=your-db-password" > .env ; explorer .
```

2. Create a new MCP server in Cursor:
```
name: supabase
protocol: command
# if pipx (recommended)
command: supabase-mcp-server
# if uv
command: uv run supabase-mcp-server
```

3. Reload Cursor
If you encounter connection issues, try closing and reopening Cursor.

#### Setup Windsurf

> 💡 **Setting environment variables**: For Windsurf, it's recommended to set environment variables directly in the `mcp_config.json` as shown below.


1. Add / modify `mcp_config.json` file:
```json
{
    "mcpServers": {
      "supabase": {
        "command": "/Users/az/.local/bin/uv",
        "args": [
          "run",
          "supabase-mcp-server"
        ],
        "env": {
          "SUPABASE_PROJECT_REF": "your-project-ref",
          "SUPABASE_DB_PASSWORD": "your-db-password"
        }
      }
    }
}
```


> 💡 **Finding UV executable path**:
> - On macOS/Linux: Run `which uv` in terminal
> - On Windows: Run `where uv` in command prompt
> The output will show the full path to use in your configuration.

### Running as a python module (if you installed it from source)

If you installed from source or want to run the development version, use this command:

```bash
uv --directory /path/to/supabase-mcp-server run python -m supabase_mcp.main
```

#### Setup Cursor
1. Create a new MCP server
2. Add the following configuration:
```
name: supabase
protocol: command
command: uv --directory /path/to/supabase-mcp-server run python -m supabase_mcp.main
```

Replace `/path/to/supabase-mcp-server` with your actual repository path, for example:
```
command: uv --directory /Users/username/projects/supabase-mcp-server run python -m supabase_mcp.main
```

#### Setup Windsurf
1. Add / modify `mcp_config.json` file:
```json
{
    "mcpServers": {
      "supabase": {
        "command": "/Users/az/.local/bin/uv",
        "args": [
          "--directory",
          "/path/to/supabase-mcp-server",
          "run",
          "python",
          "-m",
          "supabase_mcp.main"
        ],
        "env": {
          "SUPABASE_PROJECT_REF": "your-project-ref",
          "SUPABASE_DB_PASSWORD": "your-db-password"
        }
      }
    }
}
```

### Configuring connection to different Supabase projects

> 💡 **Tip**: Connection to local Supabase project is configured out of the box. You don't need to set environment variables.

To connect to a different Supabase project, you need to set environment variables:
- `SUPABASE_PROJECT_REF`
- `SUPABASE_DB_PASSWORD`

The recommended way to set these variables depends on your IDE:
- **For Windsurf**: Set them directly in `mcp_config.json` (cleanest approach)
- **For Cursor**: Set them using global config directory (see [Setup Cursor](#setup-cursor))
- **For local development**: Use `.env` in the project root (when installed from source)

#### Local Supabase project

If no configuration is provided, the server defaults to local Supabase settings:
- Host: `127.0.0.1:54322`
- Password: `postgres`

This works out of the box with Supabase CLI's local development setup.

#### Remote Supabase project (staging / production)

##### When using Windsurf
Set the environment variables directly in your `mcp_config.json`:
```json
{
    "mcpServers": {
      "supabase": {
        "command": "/Users/az/.local/bin/uv",
        "args": [
          "run",
          "supabase-mcp-server"
        ],
        "env": {
          "SUPABASE_PROJECT_REF": "your-project-ref",
          "SUPABASE_DB_PASSWORD": "your-db-password"
        }
      }
    }
}
```

##### When using Cursor
Create a global config file:
```bash
# Create config directory and navigate to it
# On macOS/Linux
mkdir -p ~/.config/supabase-mcp && cd ~/.config/supabase-mcp
# On Windows (in PowerShell)
mkdir -Force "$env:APPDATA\supabase-mcp" ; cd "$env:APPDATA\supabase-mcp"

# Create and open .env file
# On macOS/Linux
echo "SUPABASE_PROJECT_REF=your-project-ref
SUPABASE_DB_PASSWORD=your-db-password" > .env && open .
# On Windows (in PowerShell)
echo "SUPABASE_PROJECT_REF=your-project-ref
SUPABASE_DB_PASSWORD=your-db-password" > .env ; explorer .
```

Then in Cursor's MCP server configuration:
```
name: supabase
protocol: command
# if pipx (recommended)
command: supabase-mcp-server
# if uv
command: uv run supabase-mcp-server
```

> 💡 **Note**: Unlike Windsurf, Cursor requires configuration via global config file or environment variables. The global config approach is recommended for better maintainability.

##### Global config
3. **Global config** (Lowest precedence)
   ```bash
   # Create in your home config directory for persistent access
   mkdir -p ~/.config/supabase-mcp
   echo "SUPABASE_PROJECT_REF=your-project-ref
   SUPABASE_DB_PASSWORD=your-db-password" > ~/.config/supabase-mcp/.env
   ```
   Perfect for developers who want to set up once and use across multiple projects.



##### When developing locally (installed from source)
Create `.env` file in the root of the cloned repository:
```bash
# In the supabase-mcp-server directory (project root)
echo "SUPABASE_PROJECT_REF=your-project-ref
SUPABASE_DB_PASSWORD=your-db-password" > .env
```
When running from source, it looks for `.env` in the project root directory (where you cloned the repository).



## Troubleshooting

Before connecting to IDEs, verify server functionality using the MCP Inspector:
```bash
# Using MCP inspector
mcp dev supabase_mcp.main

# Or run directly
uv --directory /path/to/supabase-mcp-server run python -m supabase_mcp.main
```
This connects to MCP Inspector which allows you to debug and test the server without a client.


## Future improvements

- 📦 Simplified installation via package manager - ✅ (0.2.0)
- 🐍 Support methods and objects available in native Python SDK
- 🔍 Improve SQL syntax validation
- Support for creating edge functions, managing secrets (similar to Loveble integration)
