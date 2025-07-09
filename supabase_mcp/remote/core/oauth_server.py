"""This module provides a simple OAuth server host implementation and CLI entrypoint.

It defines default configuration values, a class to encapsulate OAuth server settings and startup logic,
and a Click-based command-line interface for launching the server.
"""

import os
import click
from mcp.server.auth.settings import AuthSettings
from mcp_oauth import (
    OAuthServer,
    SimpleAuthSettings,
    AuthServerSettings,
    IntrospectionTokenVerifier,
)
from ..fast_api.environment import FastApiEnvironment

DEFAULT_OAUTH_HOST: str = "127.0.0.1"
DEFAULT_OAUTH_PORT: int = 9080
DEFAULT_EXPOSE_OAUTH_SERVER_URL: str | None = None


class SimpleOAuthServerHost:
    """
    SimpleOAuthServerHost encapsulates the configuration and startup logic for a simple OAuth server.

    Attributes:
        mcp_server_url (str): Root url address of mcp server that will be use this Oauth Host
        oauth_host (str): Host address for the OAuth server.
        oauth_port (int): Port number for the OAuth server.
        oauth_server_url (str): Internal URL for the OAuth server.
        superusername (str | None): Superuser username for authentication.
        superuserpassword (str | None): Superuser password for authentication.
        expose_oauth_server_url (str): Publicly exposed URL for the OAuth server.
    """

    def __init__(
        self,
        mcp_server_url: str,
        oauth_host: str = DEFAULT_OAUTH_HOST,
        oauth_port: int = DEFAULT_OAUTH_PORT,
        expose_oauth_server_url: str | None = DEFAULT_EXPOSE_OAUTH_SERVER_URL,
        superusername: str | None = os.getenv("SUPERUSERNAME"),
        superuserpassword: str | None = os.getenv("SUPERUSERPASSWORD"),
    ):
        """Initializes the SimpleOAuthServerHost with configuration for the OAuth server.

        Args:
            mcp_server_url (str): Root url address of mcp server that will be use this Oauth Host
            oauth_host (str): Host address for the OAuth server.
            oauth_port (int): Port number for the OAuth server.
            expose_oauth_server_url (str | None): Publicly exposed URL for the OAuth server.
            superusername (str | None): Superuser username for authentication.
            superuserpassword (str | None): Superuser password for authentication.
        """
        self.mcp_server_url: str = mcp_server_url
        self.oauth_host: str = oauth_host
        self.oauth_port: int = 9080
        self.oauth_server_url: str = f"http://{oauth_host}:{oauth_port}"
        self.superusername: str = superusername
        self.superuserpassword: str = superuserpassword

        self.expose_oauth_server_url: str = (
            f"http://{oauth_host}:{oauth_port}"
            if expose_oauth_server_url is None
            else expose_oauth_server_url
        )
        """If oauthserver is exposed out the same container of the mcp server, then this value should be set to the public URL of the oauth server."""

    @property
    def mcp_auth_field(self) -> AuthSettings:
        """Returns an AuthSettings instance configured for the MCP server.

        This property constructs the AuthSettings object using the current server settings,
        the required scopes from the authentication settings, and the resource server URL
        from the FastApiEnvironment.
        """
        return AuthSettings(
            issuer_url=self.server_settings.server_url,
            required_scopes=[self.auth_settings.mcp_scope],
            resource_server_url=(
                FastApiEnvironment.DNS
                if FastApiEnvironment.DNS is not None
                else FastApiEnvironment.EXPOSE_IP
            ),
        )

    @property
    def token_verifier(self) -> IntrospectionTokenVerifier:
        port: int = 8000
        server_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

        # Authorization Server settings
        auth_server_url: AnyHttpUrl = AnyHttpUrl(f"{OAUTH_SERVER_URL}")
        auth_server_introspection_endpoint: str = f"{OAUTH_SERVER_URL}/introspect"

        # MCP settings
        mcp_scope: str = "user"

        # RFC 8707 resource validation
        oauth_strict: bool = False

        token_verifier = IntrospectionTokenVerifier(
            introspection_endpoint="self.oauth_server_url/introspect",
            server_url=str(settings.server_url),
            validate_resource=settings.oauth_strict,  # Only validate when --oauth-strict is set
        )
        return IntrospectionTokenVerifier()

    @property
    def server_settings(self) -> AuthServerSettings:
        return AuthServerSettings(
            host=self.oauth_host,
            port=self.oauth_port,
            server_url=f"{self.oauth_server_url}",
            auth_callback_path=f"{self.oauth_server_url}/login",
        )

    @property
    def auth_settings(self) -> SimpleAuthSettings:
        return SimpleAuthSettings(
            superusername=self.superusername,
            superuserpassword=self.superuserpassword,
            mcp_scope="user",
        )

    def run_oauth_server(self):
        oauth_server: OAuthServer = OAuthServer(
            server_settings=self.server_settings,
            auth_settings=self.auth_settings,
        )
        oauth_server.run_starlette_server()


@click.command()
@click.option("--port", default=9080, help="Port to listen on")
def main(port: int):
    simple_oauth_server_host: SimpleOAuthServerHost = SimpleOAuthServerHost(
        oauth_port=port
    )
    simple_oauth_server_host.run_oauth_server()


if __name__ == "__main__":
    main()
