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
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg" alt="Python 3.12+" /></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/uv-package%20manager-blueviolet" alt="uv package manager" /></a>
  <a href="https://smithery.ai/server/@alexander-zuev/supabase-mcp"><img src="https://smithery.ai/badge/@alexander-zuev/supabase-mcp" alt="smithery badge" /></a>
  <a href="https://modelcontextprotocol.io/introduction"><img src="https://img.shields.io/badge/MCP-Server-orange" alt="MCP Server" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License" /></a>
</p>



Implementation of Supabase MCP server that enables Cursor and Windsurf to interact directly with Supabase PostgreSQL database. It provides a set of database management tools that work seamlessly with these IDEs through the MCP protocol.

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

You can install Supabase MCP Server either using a package manager (recommended) or from source.

### Migration from 0.1.0 to 0.2.0
The simplest way to migrate is to do a clean install using package manager:
```bash
# Remove old installation
rm -rf supabase-mcp-server

# Install via UV (recommended)
uv pip install supabase-mcp-server
```

However you can still install from source if you prefer.

### Using Package Managers (Recommended)

```bash
# Using UV
uv pip install supabase-mcp-server

# Using pipx
pipx install supabase-mcp-server

```

Why these package managers?
- `pipx`: Installs CLI tools in isolated environments, making them available globally without conflicts
- `uv`: Fast, reliable Python package installer with dependency resolution, perfect for development

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

### Installing via Smithery (not tested)

To install Supabase MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@alexander-zuev/supabase-mcp):

```bash
npx -y @smithery/cli install @alexander-zuev/supabase-mcp --client claude
```


## Running Supabase MCP Server

This MCP server was designed to be used with AI IDEs like Cursor and Windsurf and not tested with other clients.

> 💡 **0.2.0 Update**: You'll need to update your IDE configuration to use the new command:
> - Old: `python main.py`
> - New: `uv run supabase-mcp-server` (if installed via package manager)
> - New: `uv --directory /path/to/supabase-mcp-server run python -m supabase_mcp.main` (if installed from source)

You can run the server in several ways:
- as a package script (if you installed it using package manager)
- as a python module (if you installed it from source)

> 💡 **0.2.0 Breaking change**: Installation and execution methods have changed to support package distribution. The server now runs as a proper Python module instead of a direct script.


### Running as a package script (if you installed it using package manager)

If you installed it using package manager, you can run the server with this command:

```bash
# UV
uv run supabase-mcp-server

# Pipx
pipx run supabase-mcp-server
```

#### Setup Cursor
1. Create a new MCP server
2. Add the following configuration:
```
name: supabase
protocol: command
command: uv run supabase-mcp-server
```

![Cursor MCP Server Setup](https://github.com/user-attachments/assets/79362170-cbba-4dcd-8d20-640d69708f74)

#### Setup Windsurf
1. Add / modify mcp_config.json file
```json
{
    "mcpServers": {
      "supabase": {
        "command": "/Users/az/.local/bin/uv",  # Path to UV executable
        "args": [
          "run",
          "supabase-mcp-server"
        ]
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
1. Add / modify mcp_config.json file:
```json
{
    "mcpServers": {
      "supabase": {
        "command": "/Users/az/.local/bin/uv",  # Path to UV executable
        "args": [
          "--directory",
          "/path/to/supabase-mcp-server",
          "run",
          "python",
          "-m",
          "supabase_mcp.main"
        ]
      }
    }
}
```
> 📝 If you get psycopg2 compilation errors, make sure you've installed PostgreSQL first!

> 💡 **Tip**: Running from source is recommended during development as it allows you to modify the code and see changes immediately.

### Connecting to different Supabase projects

> 💡 **Tip**: Connection to local Supabase project is configured out of the box. You don't need to configure anything.

#### Local Supabase project

If no configuration is provided, the server defaults to local Supabase settings:
- Host: `127.0.0.1:54322`
- Password: `postgres`

This works out of the box with Supabase CLI's local development setup.

#### Remote Supabase project (staging / production)

The server needs configuration to connect to your Supabase project. Configuration handling differs based on your installation method:

##### When installed via package manager

You have three options to configure the connection (in order of precedence):

1. **Environment variables** (Highest precedence)
   ```bash
   # Set directly in your shell
   export SUPABASE_PROJECT_REF=your-project-ref
   export SUPABASE_DB_PASSWORD=your-db-password
   ```

2. **Current directory** (Project-specific)
   ```bash
   # Create .env.mcp in your project directory
   # Using .env.mcp instead of .env to avoid conflicts with your project's own .env
   echo "SUPABASE_PROJECT_REF=your-project-ref
   SUPABASE_DB_PASSWORD=your-db-password" > .env.mcp
   ```
   When using package script (uv run supabase-mcp-server), looks in Cursor's working directory.
   This is ideal when using with Cursor/Windsurf as the config will be in your workspace.

3. **Global config** (Lowest precedence)
   ```bash
   # Create in your home config directory for persistent access
   mkdir -p ~/.config/supabase-mcp
   echo "SUPABASE_PROJECT_REF=your-project-ref
   SUPABASE_DB_PASSWORD=your-db-password" > ~/.config/supabase-mcp/.env.mcp
   ```
   Perfect for developers who want to set up once and use across multiple projects.

##### When installed from source

Create `.env.mcp` file in the root of the cloned repository:
```bash
# In the supabase-mcp-server directory (project root)
echo "SUPABASE_PROJECT_REF=your-project-ref
SUPABASE_DB_PASSWORD=your-db-password" > .env.mcp
```
When running from source, it looks for `.env.mcp` in the project root directory (where you cloned the repository).

> 💡 **Why .env.mcp?**: I use `.env.mcp` instead of `.env` to clearly indicate this is for the MCP server and avoid conflicts with other `.env` files in your environment.



## Troubleshooting

Before connecting to IDEs, verify server functionality using the MCP Inspector:
```bash
mcp dev main.py
```
This connects to MCP Inspector which allows you to debug and test the server without a client.

Start the development server to verify functionality:
```bash
# Using MCP inspector
mcp dev supabase_mcp.main

# Or run directly
uv --directory /path/to/supabase-mcp-server run python -m supabase_mcp.main
```

## Future improvements
- 🐍 Support methods and objects available in native Python SDK
- 🔍 Improve SQL syntax validation
- 📦 Simplified installation via package manager - ✅ (0.2.0)
- Support for creating edge functions, managing secrets (similar to Loveble integration)
