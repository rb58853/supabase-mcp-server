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
    def get_table_schema_query(schema_name: str, table: str) -> str:
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
                ON pc.relname = '{table}'
                AND pc.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = '{schema_name}')
            WHERE c.table_schema = '{schema_name}'
                AND c.table_name = '{table}'
            ORDER BY c.ordinal_position;
        """

    @staticmethod
    def get_table_stats_query(schema_name: str, table_name: str) -> str:
        """Returns SQL query to get table statistics like row count, size, etc"""
        return f"""
            SELECT 
                pg_size_pretty(pg_total_relation_size('{schema_name}.{table_name}')) as total_size,
                pg_size_pretty(pg_table_size('{schema_name}.{table_name}')) as table_size,
                pg_size_pretty(pg_indexes_size('{schema_name}.{table_name}')) as index_size,
                (SELECT reltuples::bigint FROM pg_class WHERE oid = '{schema_name}.{table_name}'::regclass) as row_estimate
        """

    @staticmethod
    def get_table_relationships_query(schema_name: str, table_name: str) -> str:
        """Returns SQL query to get foreign key relationships"""
        return f"""
            SELECT
                tc.table_schema as schema_name,
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_schema AS foreign_schema_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = '{schema_name}'
                AND tc.table_name = '{table_name}';
        """

    @staticmethod
    def get_table_indexes_query(schema_name: str, table_name: str) -> str:
        """Returns SQL query to get index information"""
        return f"""
            SELECT
                i.relname as index_name,
                a.attname as column_name,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary
            FROM pg_class t
            JOIN pg_index ix ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_attribute a ON a.attrelid = t.oid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE t.relkind = 'r'
                AND n.nspname = '{schema_name}'
                AND t.relname = '{table_name}'
                AND a.attnum = ANY(ix.indkey)
            ORDER BY ix.indisprimary DESC, ix.indisunique DESC, i.relname;
        """
