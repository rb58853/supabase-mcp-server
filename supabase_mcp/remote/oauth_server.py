import click
from mcp_oauth import QuickOAuthServerHost

@click.command()
@click.option("--host", default="127.0.0.1", help="")
@click.option("--port", default=9080, help="Port to listen on")
@click.option("--superusername", default=None, help="")
@click.option("--superuserpassword", default=None, help="")
def main(
    host: str,
    port: int,
    superusername: str | None,
    superuserpassword: str | None,
):
    simple_oauth_server_host: QuickOAuthServerHost = QuickOAuthServerHost(
        oauth_port=port,
        oauth_host=host,
        superusername=superusername,
        superuserpassword=superuserpassword,
    )
    simple_oauth_server_host.run_oauth_server()


if __name__ == "__main__":
    main()