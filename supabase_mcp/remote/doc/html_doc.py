from ..fast_api.environment import FastApiEnvironment

end: str = """
</html>
"""

base: str = """<html>

<head>
    <style>
        :root {
            --bg-primary: #1E1E1E;
            --text-primary: #abb2bf;
            --heading-color: #61afef;
            --accent-color: #98c379;
            --border-color: #404452;
            --shadow-color: rgba(0, 0, 0, 0.3);
        }

        /* Estilos base del cuerpo */
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;

            /* Modificaciones para modo oscuro */
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }

        /* Estilos de encabezados */
        h1 {
            color: var(--heading-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
        }

        h2 {
            color: #89ddff;
            /* Azul más claro que h1 */
            padding-bottom: 8px;
            margin: 1.2em 0 0.8em;
            font-size: 1.5em;
        }

        h3 {
            color: #c792ea;
            /* Tonalidad morada suave */
            padding-bottom: 4px;
            margin: 1em 0 0.5em;
            font-size: 1.25em;
        }

        /* Estilos adicionales para mejor legibilidad */
        p {
            margin: 1em 0;
            opacity: 0.95;
        }

        pre {
            background-color: rgba(98, 151, 219, 0.1);
            border-radius: 8px;
            padding: 1em;
            overflow-x: auto;
        }

        li code {
            background-color: rgba(255, 30, 127, 0.1);
            /* Rosa muy suave con opacidad */
            color: rgb(255, 0, 111);
            /* Rosa muy suave con opacidad */
            padding: 0px;
            padding-inline: 5px;
            border-radius: 3px;
        }
        
        .inline-code {
            background-color: rgba(255, 30, 127, 0.1);
            /* Rosa muy suave con opacidad */
            color: rgb(255, 0, 111);
            /* Rosa muy suave con opacidad */
            padding: 0px;
            padding-inline: 5px;
            border-radius: 3px;
        }
        
        .horizontal-ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .horizontal-ul li {
            display: inline-block;
            padding: 0 10px;
        }

        /* Estilo principal del código */
        code {
            font-family: 'Consolas', Monaco, 'Andale Mono', monospace;
            line-height: 1.5;
        }

        /* Estilos para los elementos destacados */
        span {
            background-color: transparent;
        }

        .lang-python {
            color: #abb2bf;
        }

        /* Palabras clave */
        .hljs-keyword {
            color: #c678dd;
        }

        /* Funciones */
        .hljs-function .hljs-title {
            color: #61afef;
        }

        /* Importaciones */
        .hljs-import {
            color: #98c379;
        }

        /* Comentarios */
        .hljs-comment {
            color: #5c6370;
            font-style: italic;
        }

        /* Strings */
        .hljs-string {
            color: #98c379;
        }

        /* Números */
        .hljs-number {
            color: #d19a66;
        }

        /* Operadores */
        .hljs-operator {
            color: #56b6c2;
        }

        /* Clases */
        .hljs-class {
            color: #e06c75;
        }

        /* Métodos */
        .hljs-method {
            color: #61afef;
        }
    </style>
</head>

<body>
    <h1 id="mcp-server-for-supabase">MCP Server for Supabase</h1>
    <p>This MCP server implements the Model Context Protocol (MCP) through HTTPstream, providing secure and efficient
        access to Supabase services. The server is designed to expose specific tools and resources that allow client
        applications to interact with the database in a structured manner.</p>
    <h2 id="main-features">Main Features</h2>
    <ul>
        <li>Exposure of services through HTTPstream</li>
        <li>Access to Supabase CRUD operations</li>
        <li>Secure connection management</li>
        <li>Interface compatible with the MCP protocol</li>
    </ul>
    <hr>
    <h1 id="tools">Tools</h1>
    <h2 id="database-tools">Database Tools</h2>
    <h3 id="get_db_schemas">get_db_schemas</h3>
    <p>Shows a summary of all databases including their size and number of tables.</p>
    <h3 id="get_tables">get_tables</h3>
    <p>Lists all tables in a specific database, showing how many records they have.</p>
    <p><strong>Required parameter</strong>:</p>
    <ul>
        <li>Database name (e.g.: &#39;public&#39;)</li>
    </ul>
    <h3 id="get_table_schema">get_table_schema</h3>
    <p>Shows detailed structure of a specific table, including columns and relationships.</p>
    <p><strong>Required parameters</strong>:</p>
    <ul>
        <li>Database name</li>
        <li>Table name</li>
    </ul>
    <h3 id="execute_postgresql">execute_postgresql</h3>
    <p>Executes SQL commands in your database.</p>
    <p><strong>Operation types</strong>:</p>
    <ul>
        <li>Read (SELECT): Safe, no special permissions</li>
        <li>Write (INSERT/UPDATE): Requires additional permissions</li>
        <li>Structural changes (CREATE/DROP): Require special confirmation</li>
    </ul>
    <p><strong>Important</strong>: All changes are automatically saved as versions.</p>
    <h3 id="retrieve_migrations">retrieve_migrations</h3>
    <p>Shows history of all database changes.</p>
    <p><strong>Useful options</strong>:</p>
    <ul>
        <li>Filter by name</li>
        <li>Limit number of results</li>
        <li>View complete SQL commands</li>
    </ul>
    <h2 id="api-tools">API Tools</h2>
    <h3 id="send_management_api_request">send_management_api_request</h3>
    <p>Allows direct calls to Supabase Management API to manage configurations and resources.</p>
    <p><strong>Main parameters</strong>:</p>
    <ul>
        <li><code>method</code>: HTTP method (GET, POST, PUT, PATCH, DELETE)</li>
        <li><code>path</code>: API path</li>
        <li><code>path_params</code>: Path parameters</li>
        <li><code>request_params</code>: Query parameters</li>
        <li><code>request_body</code>: Request body</li>
    </ul>
    <h3 id="get_management_api_spec">get_management_api_spec</h3>
    <p>Shows complete specification of Supabase Management API.</p>
    <p><strong>Uses</strong>:</p>
    <ul>
        <li>Get entire specification</li>
        <li>Consult specific endpoint</li>
        <li>View all paths and methods</li>
        <li>Explore by domains (Analytics, Auth, Database, etc.)
            Security: Secure operation, no risks.</li>
    </ul>
    <h2 id="logs-and-analytics-tools">Logs and Analytics Tools</h2>
    <h3 id="retrieve_logs">retrieve_logs</h3>
    <p>Retrieves logs from your Supabase project services for debugging and monitoring.</p>
    <p><strong>Available collections</strong>:</p>
    <ul>
        <li><code>postgres</code>: Database server logs</li>
        <li><code>api_gateway</code>: API request and response logs</li>
        <li><code>auth</code>: Authentication and authorization logs</li>
        <li><code>postgrest</code>: REST API service logs</li>
        <li><code>pooler</code>: Connection pooling logs</li>
        <li><code>storage</code>: Storage service logs</li>
        <li><code>realtime</code>: Real-time subscription logs</li>
        <li><code>edge_functions</code>: Serverless function logs</li>
        <li><code>cron</code>: Scheduled job logs</li>
        <li><code>pgbouncer</code>: Connection pooler logs</li>
    </ul>
    <p><strong>Main parameters</strong>:</p>
    <ul>
        <li><code>collection</code>: Log collection to query (required)</li>
        <li><code>limit</code>: Maximum number of entries (default: 20)</li>
        <li><code>hours_ago</code>: Hours of logs to retrieve (default: 1)</li>
        <li><code>filters</code>: List of filters for log filtering</li>
        <li><code>search</code>: Text to search in event messages</li>
        <li><code>custom_query</code>: Custom SQL query</li>
    </ul>
    <p><strong>How it works</strong>: Makes a request to Supabase Management API to get logs, using predefined or custom
        queries depending on the selected collection.</p>
    <h3 id="retrieve_advisor_analytics">retrieve_advisor_analytics</h3>
    <p>Get advisor analytics from the database.</p>
    <h2 id="security-tools">Security Tools</h2>
    <h3 id="live_dangerously">live_dangerously</h3>
    <p>Switches between safe and unsafe mode for Management API or Database operations.</p>
    <p><strong>Security modes</strong>:</p>
    <ul>
        <li><strong>Database</strong>:<ul>
                <li>Safe mode (default): Only read operations like SELECT</li>
                <li>Unsafe mode: Allows INSERT, UPDATE, DELETE and schema changes</li>
            </ul>
        </li>
        <li><strong>API</strong>:<ul>
                <li>Safe mode (default): Only stateless operations</li>
                <li>Unsafe mode: Allows state-changing operations</li>
            </ul>
        </li>
    </ul>
    <h3 id="confirm_destructive_operation">confirm_destructive_operation</h3>
    <p>Executes a destructive operation after confirmation.</p>
    <p><strong>How it works</strong>:</p>
    <ul>
        <li>Executes previously rejected high-risk operation</li>
        <li>No need to rewrite the query</li>
        <li>Confirmation IDs expire after 5 minutes</li>
    </ul>
    <p><strong>Parameters</strong>:</p>
    <ul>
        <li><code>operation_type</code>: Type of operation (&quot;api&quot; or &quot;database&quot;)</li>
        <li><code>confirmation_id</code>: ID provided in error message</li>
        <li><code>user_confirmation</code>: True to confirm execution</li>
    </ul>
    <h3 id="get_management_api_safety_rules">get_management_api_safety_rules</h3>
    <p>Shows all safety rules for Supabase Management API.</p>
    <p><strong>Provided information</strong>:</p>
    <ul>
        <li>Blocked operations</li>
        <li>Unsafe operations</li>
        <li>Safe operations</li>
    </ul>
    <p><strong>Each rule includes</strong>:</p>
    <ul>
        <li>HTTP method and path pattern</li>
        <li>Security level explanation</li>
        <li>Assigned security level</li>
    </ul>
    <h2 id="python-sdk-tools">Python SDK Tools</h2>
    <h3 id="get_auth_admin_methods_spec">get_auth_admin_methods_spec</h3>
    <p>Shows complete specification of Auth Admin methods from Python SDK.</p>
    <p><strong>Provided information</strong>:</p>
    <ul>
        <li>Method names and descriptions</li>
        <li>Required and optional parameters</li>
        <li>Parameter types and restrictions</li>
        <li>Return value information</li>
    </ul>
    <h3 id="call_auth_admin_method">call_auth_admin_method</h3>
    <p>Allows secure and validated calls to Auth Admin methods from Python SDK.</p>
    <p><strong>Main functionalities</strong>:</p>
    <ul>
        <li>User management (create, update, delete)</li>
        <li>List and search users</li>
        <li>Generate authentication links</li>
        <li>Manage multi-factor authentication</li>
    </ul>
    <p><strong>Available methods</strong>:</p>
    <ul>
        <li><code>get_user_by_id</code>: Get user by ID</li>
        <li><code>list_users</code>: List users with pagination</li>
        <li><code>create_user</code>: Create new user</li>
        <li><code>delete_user</code>: Delete user by ID</li>
        <li><code>invite_user_by_email</code>: Send invitation link</li>
        <li><code>generate_link</code>: Generate authentication links</li>
        <li><code>update_user_by_id</code>: Update user attributes</li>
        <li><code>delete_factor</code>: Delete authentication factor</li>
    </ul>
</body>
"""


def server_info(
    name: str,
    description: str,
    tools: list[str],
    is_auth: bool = False,
) -> str:
    http_path = f"{FastApiEnvironment.DNS if FastApiEnvironment.DNS else FastApiEnvironment.EXPOSE_IP}/{name}/mcp"
    text: str = f"""
    <body>
    <h2>MCP server {name}</h2>
    <p>{description}</p>
    <b>http path:</b><code class = "inline-code">{http_path}</code>
    <h3>Aviable Tools</h3>
    <ul class = "horizontal-ul">
    """
    for tool in tools:
        text += f"<li><code>{tool}</code></li>"
    text += "</ul>"

    text += (
        f""" <h3>Server Config</h3>
    You can use <a href="https://github.com/rb58853/python-mcp-client">mcp-llm-client</a> and paste this configuration
    <pre><code class="lang-python">
    <span class="hljs-string">"supabase_{name}"</span>: """
        + "{"
        + f"""
        <span class="hljs-string">"transport"</span>: <span class="hljs-string">"httpstream"</span>,
        <span class="hljs-string">"httpstream-url"</span>: <span class="hljs-string">"{http_path}"</span>,
        <span class="hljs-string">"name"</span>: <span class="hljs-string">"supabase_{name}"</span>,
        <span class="hljs-string">"description"</span>: <span class="hljs-string">"{description}"</span>
        <span class="hljs-string">"auth"</span>: <span class="hljs-string"><a href="https://github.com/rb58853/mcp-llm-client">*****</a></span>
    """
        + """}
    </code></pre>"""
    )
    return text + "</body>"
