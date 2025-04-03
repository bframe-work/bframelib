SELECT *
{% if _BF_BRANCH_SOURCE_EXIST == true %}
FROM brch.pricebooks
{% else %}
FROM src.pricebooks
{% endif %}
WHERE org_id = _BF_ORG_ID
    AND env_id = _BF_ENV_ID
    AND branch_id = _BF_BRANCH_ID
    AND created_at <= _BF_BRANCH_SYSTEM_DT
{% if _BF_PRICEBOOK_IDS|length > 0 %}
    AND durable_id IN _BF_PRICEBOOK_IDS
{% endif %}