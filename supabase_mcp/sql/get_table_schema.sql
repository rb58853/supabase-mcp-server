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