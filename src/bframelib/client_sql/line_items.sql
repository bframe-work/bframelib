SELECT *
FROM bframe.fixed_line_items
UNION -- This should be UNION ALL, but there is a bug in duckdb preventing this 11/8/2024
SELECT *
FROM bframe.event_line_items