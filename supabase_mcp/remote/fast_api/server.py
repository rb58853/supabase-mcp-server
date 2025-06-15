import contextlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .environment import FastApiEnvironment
from ..doc.httpstream_doc import root, end
from typing import Optional
from ...logger import setup_logger

# from loguru import logger

logger = setup_logger()


def httpstream_api() -> FastAPI:
    """
    Inicializa la aplicación FastAPI con configuración básica y middleware.
    """

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        servers = [
            server_mcp.mcp_server for server_mcp in FastApiEnvironment.MCP_SERVERS
        ]
        async with contextlib.AsyncExitStack() as stack:
            for server in servers:
                await stack.enter_async_context(server.session_manager.run())
            yield

    # Configuración básica
    app = FastAPI(
        lifespan=lifespan,
        title="API de Servicios MCP",
        description="API para servicios de procesamiento",
        version="1.0.0",
        docs_url="/docs",
        # redoc_url="/redoc"
    )

    for server_mcp in FastApiEnvironment.MCP_SERVERS:
        app.mount(f"/{server_mcp.name}", server_mcp.mcp_server.streamable_http_app())

    # Middleware CORS
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=["*"],
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )

    # Gestión de errores
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        logger.error(f"Error {exc.status_code}: {exc.detail}")
        return {"error": exc.detail, "status_code": exc.status_code}

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
            help_text: str = root + "\n"
            for server in FastApiEnvironment.MCP_SERVERS:
                help_text += server.help_html_text + "\n"

            return HTMLResponse(content=help_text + end, status_code=200)
        except Exception as e:
            logger.error(f"Error al generar docs: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

   
    return app
