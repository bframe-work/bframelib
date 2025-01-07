{% if _BF_BRANCH_ID == 1 %}
SELECT * EXCLUDE(rank)
FROM (
    SELECT raw.*, ROW_NUMBER() OVER(
        PARTITION BY raw.id
        ORDER BY raw.version DESC
    ) AS rank
    FROM (
        SELECT *
        FROM bframe._raw_products
    ) AS raw
)
WHERE rank = 1
{% else %}
SELECT * EXCLUDE(rank)
FROM (
    SELECT raw.*, ROW_NUMBER() OVER(
        PARTITION BY raw.id
        ORDER BY raw.version DESC
    ) AS rank
    FROM (
        SELECT *
        FROM bframe._raw_products
        UNION ALL
        SELECT *
        FROM bframe._local_products
    ) AS raw
)
WHERE rank = 1
{% endif %}