FROM python:3.12-slim-bookworm

WORKDIR /app

# Install PostgreSQL client libraries (required for psycopg2) and curl for uv installation
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# # Install uv with fixed version
ENV UV_VERSION="0.6.1"
ADD https://astral.sh/uv/${UV_VERSION}/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# # Copy the project into the image
COPY . /app
WORKDIR /app

# Create venv and install dependencies with version set
ENV SETUPTOOLS_SCM_PRETEND_VERSION="0.3.6"
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install .

# Set the entrypoint to use the venv
ENTRYPOINT ["uv", "run", "supabase-mcp-server"]
