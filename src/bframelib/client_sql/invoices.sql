SELECT
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
    SUM(COALESCE(li.amount, 0.0)) as total
FROM bframe.line_items AS li
GROUP BY ALL