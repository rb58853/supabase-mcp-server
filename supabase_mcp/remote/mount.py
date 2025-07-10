import asyncio
import click
from uvicorn import Config, Server
from default_servers import httpstream_api, DefaultServers
from ..logger import logger


@click.command()
@click.option("--port", default=8080, help="Port to listen on")
@click.option("--host", default="127.0.0.1", help="Host to hosted on")
@click.option("--protocol", default="http", help="http or https protocol")
def main(port: int, host: str, protocol: str):
    url: str = f"{protocol}://{host}:{port}"
    DefaultServers(root_mcp_server_url=url).initialize()
    fast_app = httpstream_api()

    async def run_server() -> None:
        config = Config(
            fast_app,
            host=host,
            port=port,
            log_level="info",
        )
        server = Server(config)

        logger.info(f"🚀 MCP Httpstream Server running on {url}")
        await server.serve()

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
