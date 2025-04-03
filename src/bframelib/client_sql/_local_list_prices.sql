SELECT *
{% if _BF_BRANCH_SOURCE_EXIST == true %}
FROM brch.list_prices
{% else %}
FROM src.list_prices
{% endif %}
WHERE org_id = _BF_ORG_ID
    AND env_id = _BF_ENV_ID
    AND branch_id = _BF_BRANCH_ID
    AND created_at <= _BF_BRANCH_SYSTEM_DT