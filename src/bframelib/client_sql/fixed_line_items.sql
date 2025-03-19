SELECT
    ps.line_item_id as id,
    _BF_ORG_ID as org_id,
    _BF_ENV_ID as env_id,
    _BF_BRANCH_ID as branch_id,
    CURRENT_TIMESTAMP as created_at,
    ps.list_price_uid,
    ps.contract_price_uid,
    ps.product_uid,
    ps.contract_id,
    ps.invoice_delivery,
    ps.started_at,
    ps.ended_at,
    ps.effective_at,
    ps.ineffective_at,
    ps.invoice_id,
    (CASE
        WHEN ps.invoice_delivery = 'ARREARS' AND _BF_RATING_AS_OF_DT >= ps.ended_at
        THEN 'FINALIZED'
        WHEN ps.invoice_delivery IN ('ADVANCED', 'ONE_TIME') AND _BF_RATING_AS_OF_DT >= ps.started_at
        THEN 'FINALIZED'
        ELSE 'DRAFT' 
    END) AS status,
    ps.quantity,
    round(
        ps.quantity
        * ps.proration_factor
        * COALESCE(CAST(ps.price AS DECIMAL), 0.0),
        2
    ) AS amount
FROM (
    SELECT
        staging.*,
        COALESCE(CAST(staging.fixed_quantity as DECIMAL), 1.0) AS quantity,
        (CASE staging.prorate
            WHEN TRUE
            THEN (
                CAST(date_diff('day', staging.effective_at, staging.ineffective_at) AS decimal)
                / CAST(date_diff('day', staging.proration_start, staging.proration_end) AS decimal)
            )
            WHEN FALSE
            THEN 1
            ELSE 1
        END) AS proration_factor
    FROM bframe.price_spans AS staging
    WHERE staging.product_type = 'FIXED'
) AS ps