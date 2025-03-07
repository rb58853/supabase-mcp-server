SELECT
    version,
    name,
    statements,
    array_length(statements, 1) AS statement_count,
    CASE
        WHEN version ~ '^[0-9]+$' THEN 'numbered'
        ELSE 'named'
    END AS version_type
FROM supabase_migrations.schema_migrations
ORDER BY
    -- For numeric versions, sort numerically
    CASE
        WHEN version ~ '^[0-9]+$'
            THEN
                (version::bigint)
        ELSE
            0
    END DESC,
    -- For named versions, sort alphabetically
    version DESC;
