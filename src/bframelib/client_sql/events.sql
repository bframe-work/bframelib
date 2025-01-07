{% if _BF_BRANCH_ID == 1 %}
-- Only return production event source
SELECT *
FROM bframe._raw_events
{% elif _BF_DEDUP_BRANCH_EVENTS %}
-- Union events and deduplicate, low performance
SELECT * EXCLUDE rank
FROM (
    SELECT raw.*, ROW_NUMBER() OVER(
        PARTITION BY raw.transaction_id
        ORDER BY raw.received_at DESC
    ) as rank
    FROM (
        SELECT *
        FROM bframe._local_events
        UNION ALL
        SELECT *
        FROM bframe._raw_events
    ) AS raw
)
WHERE rank = 1
{% else %}
-- Union the branch events with the production event source (still performant)
SELECT *
FROM bframe._local_events
UNION ALL
SELECT *
FROM bframe._raw_events
{% endif %}
