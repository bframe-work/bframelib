{% if _BF_READ_MODE in ('VIRTUAL', 'HYBRID', 'UNSTORED_VIRTUAL') %}
SELECT
    li.invoice_id as id,
    _BF_ORG_ID as org_id,
    _BF_ENV_ID as env_id,
    _BF_BRANCH_ID as branch_id,
    CURRENT_TIMESTAMP as created_at,
    li.contract_id,
    li.invoice_delivery,
    li.started_at,
    li.ended_at,
    (CASE
        WHEN li.invoice_delivery = 'ARREARS' AND _BF_RATING_AS_OF_DT >= li.ended_at
        THEN 'FINALIZED'
        WHEN li.invoice_delivery IN ('ADVANCED', 'ONE_TIME') AND _BF_RATING_AS_OF_DT >= li.started_at
        THEN 'FINALIZED'
        ELSE 'DRAFT' 
    END) AS status,
    round(SUM(COALESCE(li.amount, 0.0)), 2) as total
FROM bframe._all_line_items AS li
GROUP BY ALL
{% endif %}
{% if _BF_READ_MODE == 'HYBRID' %}
UNION ALL
{% endif %}
{% if _BF_READ_MODE in ('STORED', 'HYBRID') %}
SELECT *
FROM bframe._raw_invoices
{% endif %}