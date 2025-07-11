from mcp_oauth import IntrospectionTokenVerifier
from .server_mcp import ServerMCP
from ...tools.registry import ToolName
from ...logger import logger
from mcp.server.auth.settings import AuthSettings
import os
import json


class DefaultServers:
    def __init__(self, mcp_server_url: str, oauth_server_url: str):
        self.oauth_server_url: str = oauth_server_url
        self.mcp_server_url: str = mcp_server_url
        self.servers: list[ServerMCP] = []
        self.__generate_servers()

    def __generate_servers(self):
        servers_data: list[dict[str, any]] = self.__get_servers_from_file()
        if servers_data is not None:
            servers_data = servers_data["servers"]
            for server in servers_data:
                exclude_tools: list[ToolName] = [
                    ToolName(tool) for tool in server["exclude_tools"]
                ]
                self.add_server(
                    name=server["name"],
                    instructions=server["description"],
                    auth=server["auth"],
                    exclude_tools=exclude_tools,
                )
        else:
            self.servers += [self.__client_server, self.__admin_server]

    @property
    def __client_server(self) -> ServerMCP:
        logger.info(
            "Server client was created because not found servers config. For delete this server use `my_default_server_instance.remove_server('client')`"
        )
        return ServerMCP(
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

    @property
    def __admin_server(self) -> ServerMCP:
        logger.info(
            "Server admin was created because not found servers config. For delete this server use `my_default_server_instance.remove_server('admin')`"
        )
        return ServerMCP(
            name="admin",
            auth_settings=self.auth_settings,
            token_verifier=self.token_verifier,
        )

    def add_server(
        self,
        name: str,
        instructions: str,
        auth: bool,
        exclude_tools: list[ToolName] = [],
    ) -> None:
        self.servers.append(
            ServerMCP(
                name=name,
                instructions=instructions,
                exclude_tools=exclude_tools,
                auth_settings=self.auth_settings if auth else None,
                token_verifier=self.token_verifier if auth else None,
            )
        )

    def remove_server(self, server: ServerMCP = None, server_name: str = None):
        if server is not None:
            self.servers.remove(server)
        elif server_name is not None:
            for server in self.servers:
                if server.name == server_name:
                    self.servers.remove(server)

    def clear_all_servers(self):
        self.servers.clear()

    @property
    def token_verifier(self) -> IntrospectionTokenVerifier:
        return IntrospectionTokenVerifier(
            introspection_endpoint=f"{self.oauth_server_url}/introspect",
            server_url=str(self.oauth_server_url),
            validate_resource=True,
        )

    @property
    def auth_settings(self) -> AuthSettings:
        """Returns an AuthSettings instance configured for the MCP server."""
        return AuthSettings(
            issuer_url=self.oauth_server_url,
            required_scopes=["user"],
            resource_server_url=self.mcp_server_url,
        )

    def __get_servers_from_file(
        self, file_path: str = "servers.remote.json"
    ) -> list[dict[str, any]] | None:
        full_path: str = os.path.join(os.getcwd(), file_path)
        if os.path.exists(full_path):
            with open(full_path, "r") as file:
                return json.load(file)
        return None
