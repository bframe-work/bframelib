SELECT *
{% if _BF_BRANCH_SOURCE_EXIST == true %}
FROM brch.contracts
{% else %}
FROM src.contracts
{% endif %}
WHERE org_id = _BF_ORG_ID
    AND env_id = _BF_ENV_ID
    AND branch_id = _BF_BRANCH_ID
    AND created_at <= _BF_BRANCH_SYSTEM_DT
{% if _BF_CONTRACT_IDS|length > 0 %}
    AND durable_id IN _BF_CONTRACT_IDS
{% endif %}
{% if _BF_CUSTOMER_IDS|length > 0 %}
    AND customer_id IN _BF_CUSTOMER_IDS
{% endif %}