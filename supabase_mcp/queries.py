class PreBuiltQueries:
    @staticmethod
    def get_schemas_query() -> str:
        """Returns SQL query to get all accessible schemas"""
        return """
        SELECT
            s.schema_name,
            COALESCE(pg_size_pretty(sum(COALESCE(
                CASE WHEN t.table_type = 'regular'
                    THEN pg_total_relation_size(
                        quote_ident(t.schema_name) || '.' || quote_ident(t.table_name)
                    )
                    ELSE 0
                END, 0)
            )), '0 B') as total_size,
            COUNT(t.table_name) as table_count
        FROM information_schema.schemata s
        LEFT JOIN (
            -- Regular tables
            SELECT
                schemaname as schema_name,
                tablename as table_name,
                'regular' as table_type
            FROM pg_tables

            UNION ALL

            -- Foreign tables
            SELECT
                foreign_table_schema as schema_name,
                foreign_table_name as table_name,
                'foreign' as table_type
            FROM information_schema.foreign_tables
        ) t ON t.schema_name = s.schema_name
        WHERE s.schema_name NOT IN ('pg_catalog', 'information_schema')
            AND s.schema_name NOT LIKE 'pg_%'
            AND s.schema_name NOT LIKE 'pg_toast%'
        GROUP BY s.schema_name
        ORDER BY
            COUNT(t.table_name) DESC,           -- Schemas with most tables first
            total_size DESC,                    -- Then by size
            s.schema_name;                      -- Then alphabetically
        """

    @staticmethod
    def get_tables_in_schema_query(schema_name: str) -> str:
        """Returns SQL query to get all tables in a schema with descriptions"""
        return f"""
            (
        -- Regular tables & views: full metadata available
        SELECT
            t.table_name,
            obj_description(pc.oid) AS description,
            pg_total_relation_size(format('%I.%I', t.table_schema, t.table_name)) AS size_bytes,
            pg_stat_get_live_tuples(pc.oid) AS row_count,
            (SELECT COUNT(*) FROM information_schema.columns c
                WHERE c.table_schema = t.table_schema
                AND c.table_name = t.table_name) AS column_count,
            (SELECT COUNT(*) FROM pg_indexes i
                WHERE i.schemaname = t.table_schema
                AND i.tablename = t.table_name) AS index_count,
            t.table_type
        FROM information_schema.tables t
        JOIN pg_class pc
            ON pc.relname = t.table_name
        AND pc.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = '{schema_name}')
        WHERE t.table_schema = '{schema_name}'
            AND t.table_type IN ('BASE TABLE', 'VIEW')
        )
        UNION ALL
        (
        -- Foreign tables: limited metadata (size & row count functions don't apply)
        SELECT
            ft.foreign_table_name AS table_name,
            (
                SELECT obj_description(
                        (quote_ident(ft.foreign_table_schema) || '.' || quote_ident(ft.foreign_table_name))::regclass
                    )
            ) AS description,
            0 AS size_bytes,
            NULL AS row_count,
            (SELECT COUNT(*) FROM information_schema.columns c
                WHERE c.table_schema = ft.foreign_table_schema
                AND c.table_name = ft.foreign_table_name) AS column_count,
            0 AS index_count,
            'FOREIGN TABLE' AS table_type
        FROM information_schema.foreign_tables ft
        WHERE ft.foreign_table_schema = '{schema_name}'
        )
        ORDER BY size_bytes DESC;
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
                c.ordinal_position,
                CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key,
                fk.foreign_table_name,
                fk.foreign_column_name
            FROM information_schema.columns c
            JOIN pg_class pc
                ON pc.relname = '{table}'
                AND pc.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = '{schema_name}')
            LEFT JOIN (
                SELECT ccu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                WHERE tc.table_schema = '{schema_name}'
                    AND tc.table_name = '{table}'
                    AND tc.constraint_type = 'PRIMARY KEY'
            ) pk ON c.column_name = pk.column_name
            LEFT JOIN (
                SELECT
                    kcu.column_name,
                    ccu.table_name as foreign_table_name,
                    ccu.column_name as foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                WHERE tc.table_schema = '{schema_name}'
                    AND tc.table_name = '{table}'
                    AND tc.constraint_type = 'FOREIGN KEY'
            ) fk ON c.column_name = fk.column_name
            WHERE c.table_schema = '{schema_name}'
                AND c.table_name = '{table}'
            ORDER BY c.ordinal_position;
        """
