"""
### Quick start httpstream mcp server.
#### Use example
```python
from supabase_mcp.remote.server import run as run_remote_server
import click

@click.command()
@click.option("--port", default=8080, help="Port to listen on")
@click.option("--host", default="127.0.0.1", help="Host to hosted on")
@click.option(
    "--oauth_url", default="http://127.0.0.1:9080", help="OAuth server expose URL"
)
def main(port: int, host: str, oauth_url: str):
    run_remote_server(port=port,host=host,oauth_url=oauth_url)

if __name__ == "__main__":
    main()
```
"""

import click
import asyncio
from uvicorn import Config, Server

if __name__ == "__main__":
    from supabase_mcp.remote.core.default_servers import DefaultServers
    from supabase_mcp.remote.core.fast_api.server import httpstream_api
    from supabase_mcp.logger import logger
else:
    from .core.default_servers import DefaultServers
    from .core.fast_api.server import httpstream_api
    from ..logger import logger


@click.command()
@click.option("--port", default=8080, help="Port to listen on")
@click.option("--host", default="127.0.0.1", help="Host to hosted on")
@click.option(
    "--oauth_url", default="http://127.0.0.1:9080", help="OAuth server expose URL"
)
def main(port: int, host: str, oauth_url: str):
    run(
        port=port,
        host=host,
        oauth_url=oauth_url,
    )


def run(port: int, host: str, oauth_url: str):
    mcp_url: str = f"http://{host}:{port}"
    default_servers: DefaultServers = DefaultServers(
        mcp_server_url=mcp_url, oauth_server_url=oauth_url
    )
    fast_app = httpstream_api(default_servers.servers)

    async def run_server() -> None:
        config = Config(
            fast_app,
            host=host,
            port=port,
            log_level="info",
        )
        server = Server(config)

        logger.info(f"🚀 MCP Httpstream Server running on {mcp_url}")
        await server.serve()

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
