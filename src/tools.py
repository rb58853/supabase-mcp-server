class PreBuiltQueries:
    @staticmethod
    def get_schemas_query() -> str:
        """Returns SQL query to get all accessible schemas"""
        return """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schema_name;
        """

    @staticmethod
    def get_tables_in_schema_query(schema_name: str) -> str:
        """Returns SQL query to get all tables in a schema with descriptions"""
        return f"""
            SELECT DISTINCT
                t.table_name,
                obj_description(pc.oid) as description
            FROM information_schema.tables t
            JOIN pg_class pc 
                ON pc.relname = t.table_name 
                AND pc.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = '{schema_name}')
            WHERE t.table_schema = '{schema_name}'
                AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_name;
        """

    @staticmethod
    def get_table_schema_query(schema_name: str, table_name: str) -> str:
        """Returns SQL query to get detailed table schema with column descriptions"""
        return f"""
            SELECT DISTINCT
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                col_description(pc.oid, c.ordinal_position) as column_description,
                c.ordinal_position
            FROM information_schema.columns c
            JOIN pg_class pc 
                ON pc.relname = '{table_name}'
                AND pc.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = '{schema_name}')
            WHERE c.table_schema = '{schema_name}'
                AND c.table_name = '{table_name}'
            ORDER BY c.ordinal_position;
        """
