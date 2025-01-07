{% if _BF_RATING_RANGE_START != '' and _BF_RATING_RANGE_END != '' %}
SELECT *
FROM bframe._all_price_spans AS ps
WHERE (
    ps.invoice_delivery = 'ARREARS' 
    AND ps.ended_at BETWEEN _BF_RATING_RANGE_START AND _BF_RATING_RANGE_END
) OR (
    ps.invoice_delivery IN ('ADVANCED', 'ONE_TIME')
    AND ps.started_at BETWEEN _BF_RATING_RANGE_START AND _BF_RATING_RANGE_END
)
{% else %}
SELECT *
FROM bframe._all_price_spans AS ps
WHERE _BF_RATING_AS_OF_DT >= ps.started_at 
    AND _BF_RATING_AS_OF_DT < ps.ended_at
{% endif %}