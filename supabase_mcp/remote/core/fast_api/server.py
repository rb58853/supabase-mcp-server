import contextlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase_mcp.remote.core.server_mcp import ServerMCP
from ..doc.html_doc import base, end
from ....logger import logger

# from ....logger import setup_logger
# logger = setup_logger()


def httpstream_api(mcp_servers: list[ServerMCP]) -> FastAPI:
    """
    Inicializa la aplicación FastAPI con configuración básica.
    """

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        servers = [server_mcp.mcp_server for server_mcp in mcp_servers]
        async with contextlib.AsyncExitStack() as stack:
            for server in servers:
                await stack.enter_async_context(server.session_manager.run())
            yield

    # Configuración básica
    app = FastAPI(
        lifespan=lifespan,
        title="API de Servicios MCP para supabase",
        description="API para servicios de procesamiento de datos usando MCP en supabase",
        version="1.0.0",
    )

    for server_mcp in mcp_servers:
        app.mount(f"/{server_mcp.name}", server_mcp.mcp_server.streamable_http_app())

    # Rutas básicas
    @app.get("/", include_in_schema=False)
    async def redirect_to_help():
        return RedirectResponse(url="/help")

    @app.get("/health", include_in_schema=True)
    async def health_check():
        return {"status": "ok"}

    @app.get("/help", include_in_schema=False)
    async def help() -> str:
        try:
            help_text: str = base + "\n<h1> Aviable Servers</h1>\n"
            for server in mcp_servers:
                help_text += server.help_html_text() + "\n"

            return HTMLResponse(content=help_text + end, status_code=200)
        except Exception as e:
            logger.error(f"Error al generar docs: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    return app
