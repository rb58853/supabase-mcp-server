root: str = """
<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }

        h1 {
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }

        code {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            display: block;
        }

        pre {
            margin: 15px 0;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
            overflow-x: auto;
        }

        .code-block {
            position: relative;
            margin: 15px 0;
        }

        .code-block::before {
            content: "python";
            position: absolute;
            top: 8px;
            right: 12px;
            background-color: #007396;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
        }
    </style>
</head>
"""

end: str = """
</html>
"""

admin: str = """
<body>
    <h1>Httpstream expuesto</h1>
    
    <p>Este servidor ofrece un MCP (Model Context Protocol) de supabase que expone sus servicios. Para usar el mismo debe usar el path 
, direccion donde estaran expuestos los recursos y tools de este servidor.</p>

    <div class="code-block">
        <pre><code>from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def main():
    # Connect to a streamable HTTP server
    async with streamablehttp_client("http://0.0.0.0:8080/server/admin") as (
        read_stream,
        write_stream,
        _,
    ):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            
            # List available resources
            resources = await session.list_resource_templates()
            
            # List available prompts
            promts = await session.list_prompts()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())</code></pre>
    </div>
</body>
"""
