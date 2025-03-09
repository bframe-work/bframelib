{% if _BF_READ_MODE in ('VIRTUAL', 'HYBRID', 'UNSTORED_VIRTUAL') %}
SELECT *
FROM bframe._all_line_items
{% endif %}
{% if _BF_READ_MODE == 'HYBRID' %}
UNION ALL
{% endif %}
{% if _BF_READ_MODE in ('STORED', 'HYBRID') %}
SELECT *
FROM bframe._raw_line_items
{% endif %}