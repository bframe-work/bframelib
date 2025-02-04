SELECT e.* EXCLUDE(org_id, env_id, branch_id),
    COALESCE(e.customer_id, c.durable_id) AS resolved_customer_id
FROM bframe.events as e
LEFT JOIN (
    SELECT c.durable_id, cia.alias, c.effective_at, c.ineffective_at
    FROM bframe.customers AS c
    JOIN (
        SELECT
            c.id,
            ci.value AS alias
        FROM bframe.customers AS c, UNNEST(json_extract_string(c.ingest_aliases, '$[*]')) AS ci(value)
        GROUP BY 1, 2
    ) AS cia ON cia.id = c.id
) AS c ON (
    c.alias = e.customer_alias
    AND (e.metered_at >= c.effective_at OR c.effective_at IS NULL)
    AND (e.metered_at < c.ineffective_at OR c.ineffective_at IS NULL)
)