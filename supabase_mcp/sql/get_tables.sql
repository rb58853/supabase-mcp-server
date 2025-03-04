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