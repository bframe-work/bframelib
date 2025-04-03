SELECT *
FROM src.contract_prices
WHERE org_id = _BF_ORG_ID
    AND env_id = _BF_ENV_ID
    AND branch_id = 1
    AND created_at <= _BF_PROD_SYSTEM_DT