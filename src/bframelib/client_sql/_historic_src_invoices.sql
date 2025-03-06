SELECT *
FROM src.invoices
WHERE org_id = _BF_ORG_ID
    AND env_id = _BF_ENV_ID
    AND branch_id = _BF_BRANCH_ID
    AND created_at <= _BF_SYSTEM_DT
    AND started_at < date_trunc('month', CAST(_BF_LOOKBACK_DT as TIMESTAMP))