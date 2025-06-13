## httpstream

### Levantar con Uvicorn

Para crear levantar el servidor `httpstream` debe levantar la api de `fastapi`, una opcion para ello es hacerlo con `uvicorn`, por ejemplo:

```shell
uvicorn supabase_mcp.remote.mount:app --host 0.0.0.0 --port 8080
```

Alternativamente puede instalar el paquete de forma local con el bash:

```shell
pytho3.x -m build
pip3.x install -e .
```

### Instalar paquete local y levantarlo en tu propio proyecto

El paquete traer por default dos servidores que se exponen. En caso de crear otro servidor asegurese de que no contenga los mismos nombres de los servidores default. Opcionalmente puede elimnar los servidores expuestos agregando la linea `clear_servers()`. Los nombres de server expuestos son `admin` y `client`.

A continuacion se muestra un ejemplo de codigo que usa el paquete. Crear un nuevo proyecto con el siguiente codigo:

```python
#main.py
from supabase_mcp import ServerMCP, FastApiEnvironment, ToolName,httpstream_api

#Originalmente existen dos MCP expuestos. Un MCP para admins y uno para clientes de solo lectura. Si desea elimnar estos  servidores debe agregar la linea
FastApiEnvironment.clear_servers()

#En caso de querer configurar un nuevo server mcp, copiar la siguiente linea pasandole parametros seleccionados o dejarlo default
ServerMCP(
    name="your_server_name",
    instructions="your server use case",
    exclude_tools=[],
    help_html_text="<body> your html text help <body>",
    use_as_server=True,
    transfer_protocol = "httpstream"
)

app = httpstream_api()
```

Si solo desea usar los servidores por defecto del paquete su codigo deberia quedar asi:

```python
#main.py
from supabase_mcp import httpstream_api
app = httpstream_api()
```

Luego en la carpeta raiz de tu nuevo proyecto levantar tu api con `uvicorn`

```shell
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Dependencias

- `fastapi`
