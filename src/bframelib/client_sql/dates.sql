SELECT *
FROM src.dates
{% if _BF_RATING_RANGE_START != '' and _BF_RATING_RANGE_END != '' %}
WHERE _BF_RATING_RANGE_START <= month_start 
    AND month_start < _BF_RATING_RANGE_END
{% endif %}