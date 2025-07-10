"""This module provides a simple OAuth server host implementation and CLI entrypoint.

It defines default configuration values, a class to encapsulate OAuth server settings and startup logic,
and a Click-based command-line interface for launching the server.
"""

import os
from mcp.server.auth.settings import AuthSettings
from mcp_oauth import (
    OAuthServer,
    SimpleAuthSettings,
    AuthServerSettings,
    IntrospectionTokenVerifier,
)

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
        oauth_host: str = DEFAULT_OAUTH_HOST,
        oauth_port: int = DEFAULT_OAUTH_PORT,
        superusername: str | None = os.getenv("SUPERUSERNAME"),
        superuserpassword: str | None = os.getenv("SUPERUSERPASSWORD"),
        mcp_scope: str = "user",
        # mcp_scopes: list[str] = ["user"],
    ):
        """Initializes the SimpleOAuthServerHost with configuration for the OAuth server.

        Args:
            oauth_host (str): Host address for the OAuth server.
            oauth_port (int): Port number for the OAuth server.
            superusername (str | None): Superuser username for authentication.
            superuserpassword (str | None): Superuser password for authentication.
        """
        self.oauth_host: str = oauth_host
        self.oauth_port: int = 9080
        self.oauth_server_url: str = f"http://{oauth_host}:{oauth_port}"
        self.superusername: str = superusername
        self.superuserpassword: str = superuserpassword
        self.mcp_scope: str = mcp_scope
        # self.mcp_scopes: list[str] = mcp_scopes

    @property
    def __auth_settings(self) -> SimpleAuthSettings:
        return SimpleAuthSettings(
            superusername=self.superusername,
            superuserpassword=self.superuserpassword,
            mcp_scope=self.mcp_scope,
        )

    @property
    def __server_settings(self) -> AuthServerSettings:
        return AuthServerSettings(
            host=self.oauth_host,
            port=self.oauth_port,
            server_url=f"{self.oauth_server_url}",
            auth_callback_path=f"{self.oauth_server_url}/login",
        )

    def run_oauth_server(self):

        oauth_server: OAuthServer = OAuthServer(
            server_settings=self.__server_settings,
            auth_settings=self.__auth_settings,
        )
        oauth_server.run_starlette_server()
