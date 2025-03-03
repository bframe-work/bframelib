SELECT *
FROM src.dates
{% if _BF_READ_MODE == 'VIRTUAL' %}
WHERE date_trunc('month', CAST(_BF_RATING_RANGE_START as TIMESTAMP)) <= month_start 
    AND _BF_RATING_RANGE_END > month_start
{% elif _BF_READ_MODE == 'CURRENT' or _BF_READ_MODE == 'UNSAVED_CURRENT' %}
WHERE date_trunc('month', CAST(_BF_LOOKBACK_DT as TIMESTAMP)) <= month_start
    AND _BF_FORWARD_DT > month_start
{% endif %}