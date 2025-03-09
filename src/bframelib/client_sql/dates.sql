SELECT *
FROM src.dates
{% if _BF_READ_MODE in ('VIRTUAL', 'UNSTORED_VIRTUAL', 'HYBRID') %}
WHERE date_trunc('month', CAST(_BF_RATING_RANGE_START as TIMESTAMP)) <= month_start 
    AND _BF_RATING_RANGE_END > month_start
{% elif _BF_READ_MODE == 'STORED' %}
WHERE 1=-1
{% endif %}