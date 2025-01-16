SELECT *
{% if _BF_BRANCH_SOURCE_EXIST == true %}
FROM brch.events
{% elif _BF_EVENTS_SOURCE_LOCAL == true %}
FROM evt.events
{% else %}
FROM src.events
{% endif %}
WHERE org_id = _BF_ORG_ID
    AND env_id = _BF_ENV_ID
    AND branch_id = _BF_BRANCH_ID
    AND received_at <= _BF_SYSTEM_DT