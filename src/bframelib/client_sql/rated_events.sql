SELECT 
    _BF_ORG_ID as org_id,
    _BF_ENV_ID as env_id,
    _BF_BRANCH_ID as branch_id,
    COALESCE(me.transaction_id, 'EMPTY_RATED_EVENT') as transaction_id,
    COALESCE(me.customer_id, ps.customer_id) as customer_id,
    COALESCE(me.properties, '{}') as properties,
    COALESCE(me.metered_at, ps.started_at) as metered_at,
    COALESCE(me.received_at, ps.started_at) as received_at,
    ps.list_price_uid,
    ps.contract_price_uid,
    ps.product_uid,
    ps.product_type,
    ps.price,
    COALESCE(me.quantity, 0) as quantity,
    ps.price::DECIMAL * COALESCE(me.quantity, 0) AS amount,
    ps.contract_id,
    ps.started_at,
    ps.ended_at,
    ps.effective_at,
    ps.ineffective_at,
    ps.invoice_id,
    ps.line_item_id,
    (CASE
        WHEN _BF_RATING_AS_OF_DT >= ps.ended_at
        THEN 'FINALIZED'
        ELSE 'DRAFT'
    END) AS status,
    ps.invoice_delivery
FROM bframe.matched_events AS me
-- We use a RIGHT JOIN to include all price_spans, we subsequently filter out any non-event based ones.
-- This creates empty rated event rows that are primarily used for empty line items.
RIGHT JOIN bframe.price_spans AS ps
    ON me.product_uid = ps.product_uid
    AND me.metered_at >= ps.effective_at 
    AND me.metered_at <  ps.ineffective_at
    AND me.customer_id = ps.customer_id
WHERE me.product_type = 'EVENT'
    OR ps.product_type = 'EVENT'