SELECT *
FROM bframe._raw_line_items
{% if _BF_READ_MODE == 'CURRENT' %}
UNION
SELECT *
FROM bframe._active_src_line_items
UNION ALL
SELECT *
FROM bframe._historic_src_line_items
{% endif %}