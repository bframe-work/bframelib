SELECT ps.*
FROM (
    SELECT aps.*,
    md5(
        CAST(_BF_ORG_ID AS TEXT)
        || CAST(_BF_ENV_ID AS TEXT)
        || CAST(_BF_BRANCH_ID AS TEXT)
        || aps.invoice_delivery::TEXT
        || aps.contract_id::TEXT
        || aps.started_at::TEXT
        || aps.ended_at::TEXT
    ) AS invoice_id,
    md5(
        CAST(_BF_ORG_ID AS TEXT)
        || CAST(_BF_ENV_ID AS TEXT)
        || CAST(_BF_BRANCH_ID AS TEXT)
        || aps.invoice_delivery::TEXT
        || aps.contract_id::TEXT
        || aps.started_at::TEXT
        || aps.ended_at::TEXT
        || COALESCE(aps.list_price_uid::TEXT, '')
        || COALESCE(aps.contract_price_uid::TEXT, '')
    ) AS line_item_id
    FROM bframe._all_price_spans AS aps
    {% if _BF_READ_MODE == 'VIRTUAL' %}
    WHERE
        aps.started_at >= _BF_RATING_RANGE_START 
        AND aps.started_at < _BF_RATING_RANGE_END
    {% else %}
    WHERE
        aps.started_at >= _BF_LOOKBACK_DT 
        AND aps.started_at < _BF_FORWARD_DT
    {% endif %}
) AS ps
{% if _BF_READ_MODE == 'CURRENT' or _BF_READ_MODE == 'UNSAVED_CURRENT' %}
LEFT JOIN bframe._active_src_invoices AS asi
    ON asi.id = ps.invoice_id
WHERE asi.id IS NULL
{% endif %}