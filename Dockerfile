FROM python:3.12-slim

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install MCP inspector
RUN npm install -g @modelcontextprotocol/inspector@0.4.1

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Create venv and install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv sync

# Command to run the server
CMD [".venv/bin/mcp", "dev", "main.py"]
