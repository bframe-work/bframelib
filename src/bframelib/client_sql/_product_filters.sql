SELECT
    f.* EXCLUDE(filter),
    COALESCE(json_extract_string(f.filter, 'path'), '') AS path,
    COALESCE(json_extract(f.filter, '_in'), '[]') AS _in,
    COALESCE(json_extract(f.filter, 'not_in'), '[]') AS not_in,
    COALESCE(json_extract(f.filter, 'optional'), 'false') AS optional
FROM (
    SELECT p.*, uf.filter
    FROM bframe.products AS p
    LEFT JOIN (
        SELECT p.id, UNNEST(json_extract(p.filters, '$.*')) AS filter
        FROM bframe.products AS p
    ) as uf ON p.id = uf.id
    WHERE p.ptype != 'FIXED'
) AS f