SELECT
    lp.id as list_price_uid,
    cp.id as contract_price_uid,
    COALESCE(cp.price, lp.price) as price,
    COALESCE(cp.invoice_delivery, lp.invoice_delivery, pb.invoice_delivery) AS invoice_delivery,
    COALESCE(cp.invoice_schedule, lp.invoice_schedule, pb.invoice_schedule) AS invoice_schedule,
    COALESCE(
        cp.started_at,
        date_trunc('month', c.started_at + to_months(COALESCE(cp.start_period, lp.start_period)::INTEGER)),
        c.started_at
    ) AS started_at,
    COALESCE(
        cp.ended_at,
        date_trunc('month', c.started_at + to_months(COALESCE(cp.end_period, lp.end_period)::INTEGER)),
        c.ended_at
    ) AS ended_at,
    pb.effective_at,
    pb.ineffective_at,
    c.effective_at as c_effective_at,
    c.ineffective_at as c_ineffective_at,
    COALESCE(cp.fixed_quantity, lp.fixed_quantity) as fixed_quantity,
    prod.ptype AS product_type,
    prod.id as product_uid,
    lp.pricebook_uid,
    c.pricebook_id as pricebook_id,
    c.id as contract_uid,
    c.durable_id as contract_id,
    c.customer_id,
    COALESCE(cp.prorate, c.prorate, lp.prorate, pb.prorate) as prorate,
    COALESCE(cp.pricing_metadata, lp.pricing_metadata) as pricing_metadata
FROM bframe.contracts AS c
-- This checks that the pricebook is within the effective range of the contract that is using it.
-- This doesn't get us much since we still need to do the date filtering within price spans, but
-- if prices is being used as a source of truth we must filter out pricebooks that would never be
-- combined with a specific contract iteration
JOIN bframe.pricebooks AS pb
    ON c.pricebook_id = pb.durable_id
    AND (
        c.ineffective_at IS NULL
        OR
        COALESCE(pb.effective_at, pb.ineffective_at) IS NULL
        OR
        (pb.effective_at >= c.effective_at AND pb.effective_at < c.ineffective_at)
        OR
        (pb.ineffective_at > c.effective_at AND pb.ineffective_at <= c.ineffective_at)
    )
JOIN bframe.list_prices AS lp 
    ON lp.pricebook_uid = pb.id
LEFT JOIN bframe.contract_prices AS cp
    ON cp.list_price_uid = lp.id AND cp.contract_uid = c.id
JOIN bframe.products AS prod ON prod.id = lp.product_uid
WHERE c.void = FALSE
UNION ALL
-- This side of the union represents prices without a list price linked to it
SELECT
    NULL as list_price_uid,
    cp.id as contract_price_uid,
    cp.price as price,
    cp.invoice_delivery,
    cp.invoice_schedule,
    COALESCE(
        cp.started_at,
        date_trunc('month', c.started_at + to_months(cp.start_period::INTEGER)),
        c.started_at
    ) AS started_at,
    COALESCE(
        cp.ended_at,
        date_trunc('month', c.started_at + to_months(cp.end_period::INTEGER)),
        c.ended_at
    ) AS ended_at,
    -- These are null, because price_spans assumes that these effective dates come
    -- from the pricebook not the contract... contract_prices have no pricebook hence it is NULL
    NULL as effective_at,
    NULL as ineffective_at,
    c.effective_at as c_effective_at,
    c.ineffective_at as c_ineffective_at,
    cp.fixed_quantity,
    prod.ptype AS product_type,
    prod.id as product_uid,
    NULL as pricebook_uid,
    c.pricebook_id,
    c.id as contract_uid,
    c.durable_id as contract_id,
    c.customer_id,
    COALESCE(cp.prorate, c.prorate) as prorate,
    cp.pricing_metadata
FROM bframe.contracts AS c
JOIN bframe.contract_prices AS cp
    ON cp.contract_uid = c.id AND cp.list_price_uid IS NULL
JOIN bframe.products AS prod ON prod.id = cp.product_uid 
WHERE c.void = FALSE