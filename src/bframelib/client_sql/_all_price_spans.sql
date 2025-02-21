SELECT 
    GREATEST(d.month_start, p.started_at) as started_at,
    (CASE
        WHEN p.invoice_delivery = 'ONE_TIME'
        THEN p.ended_at
        ELSE LEAST(
            DATE_TRUNC('month', d.month_start + TO_MONTHS(p.invoice_schedule::INTEGER)),
            p.ended_at
        ) 
    END) as ended_at,
    GREATEST(COALESCE(c_effective_at, p.started_at), d.month_start) as effective_at,
    (CASE
        WHEN p.invoice_delivery = 'ONE_TIME'
        THEN p.ended_at -- Matches ended_at
        WHEN p.invoice_delivery = 'ADVANCED'
        THEN LEAST(
            DATE_TRUNC('month',  d.month_start + TO_MONTHS(p.invoice_schedule::INTEGER)),
            p.ended_at
        ) -- Matches ended_at. An advanced charge can not be edited or SCD'd. Why? Because you charge it up front. Once you collect funds on it you can not edit it further
        ELSE LEAST(
            COALESCE(p.c_ineffective_at, p.ended_at),
            DATE_TRUNC('month', d.month_start + TO_MONTHS(p.invoice_schedule::INTEGER))
        ) -- ARREARS case using ineffective periods
    END) as ineffective_at,
    d.month_start as proration_start, -- we only care about full months for proration starts
    (CASE
        WHEN p.invoice_delivery = 'ONE_TIME'
        THEN p.ended_at -- Matches ended_at
        ELSE DATE_TRUNC('month', d.month_start + TO_MONTHS(p.invoice_schedule::INTEGER))
    END) as proration_end,
    p.price,
    p.pricing_metadata,
    p.fixed_quantity,
    p.product_type,
    p.invoice_delivery,
    p.prorate,
    p.list_price_uid,
    p.contract_price_uid,
    p.product_uid,
    p.pricebook_id,
    p.contract_id,
    p.contract_uid,
    p.customer_id
FROM bframe.prices AS p
JOIN bframe.dates AS d
    ON p.c_effective_at < (d.month_end + to_days(1)) -- effective date will always be larger than started so we will always use it if it exists
    AND (COALESCE(p.c_ineffective_at, p.ended_at) > d.month_start OR COALESCE(p.c_ineffective_at, p.ended_at) IS NULL)
    AND p.started_at < (d.month_end + to_days(1))
    AND (p.ended_at > d.month_start OR p.ended_at IS NULL)
    -- always use the smaller ineffective date since it's an override
    -- the ended_at is exclusive, so the ended_at date cannot equal the month_start...
    -- since this would imply that the started_at date WOULD have to be the month start
    AND COALESCE(p.effective_at, p.started_at) < (d.month_end + to_days(1))
    AND (COALESCE(p.ineffective_at, p.ended_at) > d.month_start OR COALESCE(p.ineffective_at, p.ended_at) IS NULL)
    -- Effective_at and ineffective_at can be set at the same time and have different affects than price scheduling. They both need to be respected
    AND (
        (
            (p.invoice_delivery IN ('ADVANCED', 'ARREARS')) AND (
                date_diff('month', d.month_start, p.started_at) % p.invoice_schedule
            ) = 0
        ) OR (
            p.invoice_delivery = 'ONE_TIME'
            AND DATE_TRUNC('month', p.started_at + TO_MONTHS(p.invoice_schedule::INTEGER)) = d.month_start -- align one time invoice with the period selected
        )
    )