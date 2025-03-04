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