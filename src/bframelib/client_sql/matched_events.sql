SELECT matches.* EXCLUDE(pattern_match)
FROM (
    SELECT
        e.transaction_id,
        e.resolved_customer_id AS customer_id,
        e.customer_alias,
        e.properties,
        e.metered_at,
        e.received_at,
        CAST(COALESCE(json_extract_string(e.properties, pf.agg_property), '1') AS DECIMAL) AS quantity,
        pf.id AS product_uid,
        pf.ptype AS product_type,
        bool_and(
            (
                json_extract_path(e.properties, pf.path) IN pf._in
                OR json_array_length(pf._in) = 0
            ) AND (
                json_extract_path(e.properties, pf.path) NOT IN pf.not_in
                OR json_array_length(pf.not_in) = 0
            ) OR (
                pf.optional = TRUE
                AND json_extract_path(e.properties, pf.path) IS NULL
            )
        ) AS pattern_match
    FROM bframe.processed_events AS e
    JOIN bframe._product_filters AS pf
        ON pf.event_name = (e.properties ->> 'name')
    GROUP BY ALL
) AS matches
WHERE pattern_match = TRUE