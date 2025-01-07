SELECT *
FROM src.contracts
WHERE org_id = _BF_ORG_ID
    AND env_id = _BF_ENV_ID
    AND branch_id = 1
    AND created_at <= _BF_SYSTEM_DT
{% if _BF_CONTRACT_IDS|length > 0 %}
    AND durable_id IN _BF_CONTRACT_IDS
{% endif %}