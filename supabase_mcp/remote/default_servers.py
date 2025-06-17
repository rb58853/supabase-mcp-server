from .mcp_server import ServerMCP
from .fast_api.server import httpstream_api
from ..tools.registry import ToolName

ServerMCP(name="admin")
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
