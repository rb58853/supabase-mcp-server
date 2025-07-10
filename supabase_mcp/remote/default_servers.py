from mcp_oauth import IntrospectionTokenVerifier
from .core.mcp_server import ServerMCP
from ..tools.registry import ToolName
from mcp.server.auth.settings import AuthSettings


class DefaultServers:
    INITIALIZED: bool = False

    def __init__(self, mcp_server_url: str, oauth_server_url: str):
        self.oauth_server_url: str = oauth_server_url
        self.mcp_server_url: str = mcp_server_url

    def initialize(self) -> None:
        if not DefaultServers.INITIALIZED:
            ServerMCP(
                name="admin",
                auth_settings=self.auth_settings,
                token_verifier=self.token_verifier,
            )

            ServerMCP(
                name="client",
                exclude_tools=[
                    ToolName.CALL_AUTH_ADMIN_METHOD,
                    ToolName.EXECUTE_POSTGRESQL,
                    ToolName.SEND_MANAGEMENT_API_REQUEST,
                    ToolName.CONFIRM_DESTRUCTIVE_OPERATION,
                    ToolName.LIVE_DANGEROUSLY,
                    ToolName.GET_AUTH_ADMIN_METHODS_SPEC,
                    ToolName.EXECUTE_POSTGRESQL,
                ],
            )
        DefaultServers.INITIALIZED = True

    @property
    def token_verifier(self) -> IntrospectionTokenVerifier:
        return IntrospectionTokenVerifier(
            introspection_endpoint=f"{self.oauth_server_url}/introspect",
            server_url=str(self.oauth_server_url),
            validate_resource=True,
        )

    @property
    def auth_settings(self) -> AuthSettings:
        """Returns an AuthSettings instance configured for the MCP server.

        This method constructs the AuthSettings object using the current server settings,
        the required scopes from the authentication settings, and the resource server URL
        from args.
        """
        return AuthSettings(
            issuer_url=self.oauth_server_url,
            required_scopes=["user"],
            resource_server_url=self.mcp_server_url,
        )
