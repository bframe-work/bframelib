SELECT *
FROM bframe._all_line_items
{% if _BF_READ_MODE in ('STORED', 'HYBRID') %}
UNION ALL
SELECT *
FROM bframe._raw_line_items
{% endif %}