SELECT *
FROM src.products
WHERE org_id = _BF_ORG_ID
    AND env_id = _BF_ENV_ID
    AND branch_id = 1
    AND created_at <= _BF_PROD_SYSTEM_DT
{% if _BF_PRODUCT_UIDS|length > 0 %}
    AND id IN _BF_PRODUCT_UIDS
{% endif %}