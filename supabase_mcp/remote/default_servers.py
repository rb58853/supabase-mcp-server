from .core.mcp_server import ServerMCP
from .fast_api.server import httpstream_api
from ..tools.registry import ToolName
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings
from .core.oauth_server import SimpleOAuthServerHost
from mcp_oauth import IntrospectionTokenVerifier


class DefaultServers:
    INITIALIZED: bool = False

    def __init__(self, root_mcp_server_url: str):
        oauth_server_host = SimpleOAuthServerHost(mcp_server_url=root_mcp_server_url)
        self.auth_settings: AuthSettings = oauth_server_host.mcp_auth_field
        self.token_verifier: TokenVerifier = oauth_server_host.token_verifier

    def generate(self) -> None:
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
