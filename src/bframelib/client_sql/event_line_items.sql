SELECT
    re.line_item_id as id,
    _BF_ORG_ID as org_id,
    _BF_ENV_ID as env_id,
    _BF_BRANCH_ID as branch_id,
    CURRENT_TIMESTAMP as created_at,
    re.list_price_uid,
    re.contract_price_uid,
    re.product_uid,
    re.contract_id,
    re.invoice_delivery,
    re.started_at,
    re.ended_at,
    re.effective_at,
    re.ineffective_at,
    re.invoice_id,
    (CASE
        WHEN _BF_RATING_AS_OF_DT >= re.ended_at
        THEN 'FINALIZED'
        ELSE 'DRAFT' 
    END) AS status,
    SUM(re.quantity) as quantity,
    round(SUM(CAST(COALESCE(re.amount, 0) AS decimal)), 2) AS amount
FROM bframe.rated_events AS re
GROUP BY ALL