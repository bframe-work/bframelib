SELECT *
{% if _BF_EVENTS_SOURCE_EXIST == true %}
FROM evt.events
{% else %}
FROM src.events
{% endif %}
WHERE org_id = _BF_ORG_ID
    AND env_id = _BF_ENV_ID
    AND branch_id = 1
    AND received_at <= _BF_SYSTEM_DT
{% if _BF_CUSTOMER_IDS|length > 0 %}
    AND customer_id IN _BF_CUSTOMER_IDS
{% endif %}