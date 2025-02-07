-- TENANCY SETUP --
INSERT INTO src.organizations (id, name) values (1, 'Big Co');
INSERT INTO src.environments (id, org_id, name) values (1, 1, 'PROD');
INSERT INTO src.branches (id, org_id, env_id, name) values (1, 1, 1, 'main');
INSERT INTO src.branches (id, org_id, env_id, name) values (2, 1, 1, 'branch_1');
INSERT INTO src.branches (id, org_id, env_id, name) values (3, 1, 1, 'branch_2');
INSERT INTO src.branches (id, org_id, env_id, archived_at, name) values (4, 1, 1, '2025-01-01', 'archived');

-- CUSTOMERS --
-- main --
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name, ingest_aliases) values (1, 1, 1, 1, '10', 'Bagel Corp', '["holy_bread", "carb_wheels", "bfast_brisbee"]');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 2, '20', 'Rack City');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name, version) values (1, 1, 1, 2, '20', 'Crack city', 1);
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 3, '30', 'Panda Town');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 4, '40', 'Mug Book');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 5, '50', 'Half cheeked up');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 6, '60', 'Enterprise sally');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 7, '70', '3 is a crowd');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 8, '80', 'Rampelstiltskin');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, effective_at, ineffective_at, name, ingest_aliases) values (1, 1, 1, 9, '90', '2023-01-01T0:00:00+00:00', '2023-12-01T0:00:00+00:00', 'Quick draw', '["first_bullet", "second_bullet"]');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, effective_at, ineffective_at, name, ingest_aliases) values (1, 1, 1, 10, '90','2023-12-01T0:00:00+00:00', '2023-12-10T0:00:00+00:00', 'Quick draw', '["first_bullet", "second_bullet", "third_bullet"]');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, effective_at, ineffective_at, name, ingest_aliases) values (1, 1, 1, 11, '90', '2023-12-10T0:00:00+00:00', '2023-12-20T0:00:00+00:00', 'Quick draw', '["second_bullet", "third_bullet"]');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, effective_at, name, ingest_aliases) values (1, 1, 1, 12, '90', '2023-12-20T0:00:00+00:00', 'Quick draw', '["third_bullet"]');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 13, '100', 'PB&J');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 14, '110', 'Long boy');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 15, '120', 'No pricebook');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 16, '130', 'Pricebook and contract non-overlapping effective dates');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 17, '140', 'NULL ended_at');
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 18, '150', 'updated filter logic');
-- branch_1 --
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name, version) values (1, 1, 2, 2, '20', 'Stack City', 2);
INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 2, 19, '160', 'Branch 2 Customer');

-- EVENTS --
-- Customer 1
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 1, 'holy_bread', '{"name": "api_call"}', '2023-12-20T18:58:35+00:00', '2023-12-20T18:58:35+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 2, 'carb_wheels', '{"name": "api_call"}', '2023-12-21T1:00:00+00:00', '2023-12-21T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 3, '10', '{"name": "api_call"}', '2023-12-21T1:00:01+00:00', '2023-12-21T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 4, '10', '{"name": "api_call"}', '2023-12-31T1:00:03+00:00', '2023-12-31T1:00:00+00:00'); -- This tests that events that occur on the last day are included
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 5, '10', '{"name": "cpu_usage", "cpu_hours": "1"}', '2023-12-20T18:58:35+00:00', '2023-12-20T18:58:35+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 6, '10', '{"name": "cpu_usage", "cpu_hours": "2"}', '2023-12-20T18:58:36+00:00', '2023-12-21T18:58:35+00:00');

-- CUSTOMER 2
-- main --
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 7, '20', '{"name": "api_call"}', '2023-06-01T1:00:00+00:00', '2023-06-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 8, '20', '{"name": "api_call"}', '2023-12-01T1:00:00+00:00', '2023-12-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 9, '20', '{"name": "api_call"}', '2023-12-21T1:00:02+00:00', '2023-12-21T1:00:00+00:00');
-- branch_1 --
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 2, 100000000, '20', '{"name": "cpu_usage", "cpu_hours": "2"}', '2023-07-01T1:00:00+00:00', '2023-07-01T1:00:00+00:00');

-- Customer 3
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 10, '30', '{"name": "api_call"}', '2023-12-01T1:00:00+00:00', '2023-12-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 11, '30', '{"name": "api_call"}', '2023-12-21T1:00:02+00:00', '2023-12-21T1:00:00+00:00');
-- Customer 4
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 12, '40', '{"name": "api_call"}', '2023-02-01T1:00:00+00:00', '2023-02-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 13, '40', '{"name": "api_call"}', '2023-03-01T1:00:00+00:00', '2023-03-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 14, '40', '{"name": "api_call"}', '2023-04-01T1:00:00+00:00', '2023-04-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 15, '40', '{"name": "api_call"}', '2023-12-01T1:00:00+00:00', '2023-12-01T1:00:00+00:00');
-- Customer 6
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 16, '60', '{"name": "api_call"}', '2023-02-01T1:00:00+00:00', '2023-02-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 17, '60', '{"name": "api_call"}', '2023-03-01T1:00:00+00:00', '2023-03-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 18, '60', '{"name": "api_call"}', '2023-04-01T1:00:00+00:00', '2023-04-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 19, '60', '{"name": "api_call"}', '2023-12-01T1:00:00+00:00', '2023-12-01T1:00:00+00:00');
-- Customer 9
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 20, 'first_bullet', '{"name": "api_call"}', '2023-11-01T10:00:00+00:00', '2023-11-01T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 21, 'second_bullet', '{"name": "api_call"}', '2023-11-01T10:00:00+00:00', '2023-11-01T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 22, 'third_bullet', '{"name": "api_call"}', '2023-11-01T10:00:00+00:00', '2023-11-01T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 23, 'first_bullet', '{"name": "api_call"}', '2023-12-01T10:00:00+00:00', '2023-12-01T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 24, 'second_bullet', '{"name": "api_call"}', '2023-12-01T10:00:00+00:00', '2023-12-01T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 25, 'third_bullet', '{"name": "api_call"}', '2023-12-01T10:00:00+00:00', '2023-12-01T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 26, 'first_bullet', '{"name": "api_call"}', '2023-12-12T10:00:00+00:00', '2023-12-12T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 27, 'second_bullet', '{"name": "api_call"}', '2023-12-12T10:00:00+00:00', '2023-12-12T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 28, 'third_bullet', '{"name": "api_call"}', '2023-12-12T10:00:00+00:00', '2023-12-12T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 29, 'first_bullet', '{"name": "api_call"}', '2023-12-29T10:00:00+00:00', '2023-12-29T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 30, 'second_bullet', '{"name": "api_call"}', '2023-12-29T10:00:00+00:00', '2023-12-29T10:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_alias, properties, metered_at, received_at) values (1, 1, 1, 31, 'third_bullet', '{"name": "api_call"}', '2023-12-29T10:00:00+00:00', '2023-12-29T10:00:00+00:00');
-- Customer 10
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 32, '100', '{"name": "api_call"}', '2023-01-01T1:00:00+00:00', '2023-01-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 33, '100', '{"name": "api_call"}', '2023-02-01T1:00:00+00:00', '2023-02-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 34, '100', '{"name": "api_call"}', '2023-03-01T1:00:00+00:00', '2023-03-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 35, '100', '{"name": "api_call"}', '2023-04-01T1:00:00+00:00', '2023-04-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 36, '100', '{"name": "api_call"}', '2023-05-01T1:00:00+00:00', '2023-05-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 37, '100', '{"name": "api_call"}', '2023-06-01T1:00:00+00:00', '2023-06-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 38, '100', '{"name": "api_call"}', '2023-07-01T1:00:00+00:00', '2023-07-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 39, '100', '{"name": "api_call"}', '2023-08-01T1:00:00+00:00', '2023-08-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 40, '100', '{"name": "api_call"}', '2023-09-01T1:00:00+00:00', '2023-09-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 41, '100', '{"name": "api_call"}', '2023-10-01T1:00:00+00:00', '2023-10-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 42, '100', '{"name": "api_call"}', '2023-11-01T1:00:00+00:00', '2023-11-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 43, '100', '{"name": "api_call"}', '2023-12-01T1:00:00+00:00', '2023-12-01T1:00:00+00:00');
-- Unknown customer
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 'abc', 'random customer_id 1', '{"name": "cpu_usage", "cpu_hours": "2"}', '2023-07-01T1:00:00+00:00', '2023-07-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 2, 'def', 'random customer_id 1', '{"name": "cpu_usage", "cpu_hours": "2"}', '2023-07-02T1:00:00+00:00', '2023-07-02T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 'ghi', 'random customer_id 2', '{"name": "cpu_usage", "cpu_hours": "2"}', '2023-07-01T1:00:00+00:00', '2023-07-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 'jkl', 'random customer_id 2', '{"name": "cpu_usage", "cpu_hours": "2"}', '2023-07-02T1:00:00+00:00', '2023-07-02T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 2, 'jkl', 'random customer_id 2', '{"name": "cpu_usage", "cpu_hours": "5"}', '2023-07-02T1:00:00+00:00', '2023-07-03T1:00:00+00:00');
-- Filter customer
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 44, '150', '{"name": "api_call", "region": "test-region"}', '2023-12-01T1:00:00+00:00', '2023-12-01T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 45, '150', '{"name": "api_call"}', '2023-12-02T1:00:00+00:00', '2023-12-02T1:00:00+00:00');
INSERT INTO src.events (org_id, env_id, branch_id, transaction_id, customer_id, properties, metered_at, received_at) values (1, 1, 1, 46, '150', '{"name": "api_call", "region": "us-east-1", "service": "sqs"}', '2023-12-03T1:00:00+00:00', '2023-12-03T1:00:00+00:00');

-- PRODUCTS --
INSERT INTO src.products (org_id, env_id, branch_id, id, name, ptype, filters, event_name) values (1, 1, 1, 1, 'API call', 'EVENT', '{}', 'api_call');
INSERT INTO src.products (org_id, env_id, branch_id, id, name, ptype) values (1, 1, 1, 2, 'Platform fee', 'FIXED');
INSERT INTO src.products (org_id, env_id, branch_id, id, name, ptype, filters, agg_property, event_name) values (1, 1, 1, 3, 'CPU usage', 'EVENT', '{}', 'cpu_hours', 'cpu_usage');
INSERT INTO src.products (org_id, env_id, branch_id, id, name, ptype) values (1, 1, 1, 4, 'Security features', 'FIXED');
INSERT INTO src.products (org_id, env_id, branch_id, id, name, ptype) values (1, 1, 1, 5, 'Dup product', 'FIXED');
INSERT INTO src.products (org_id, env_id, branch_id, id, name, ptype, version) values (1, 1, 1, 5, 'Dup product', 'FAKE', 1);
INSERT INTO src.products (org_id, env_id, branch_id, id, name, ptype, filters, event_name) values (1, 1, 1, 6, 'CPU usage', 'EVENT', '{"filter_1": {"path": "$.region", "_in": [], "not_in": ["test-region"], "optional": true}, "filter_2": {"path": "$.service", "_in": ["sqs"], "not_in": [], "optional": false}}', 'api_call');
INSERT INTO src.products (org_id, env_id, branch_id, id, name, ptype) values (1, 1, 2, 7, 'Separate branch: Platform fee', 'FIXED');

-- PRICEBOOKS --
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule) values (1, 1, 1, 1, '10', 'test1', 'ARREARS', 1);
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule) values (1, 1, 1, 2, '20', 'test2', 'ARREARS', 1);
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule) values (1, 1, 1, 3, '30', 'test3', 'ARREARS', 3);
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule) values (1, 1, 1, 4, '40', 'test4', 'ARREARS', 2);
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule) values (1, 1, 1, 5, '50', 'test5', 'ARREARS', 1);
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule, ineffective_at) values (1, 1, 1, 6, '60', 'test6', 'ARREARS', 1, '2023-04-30');
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule, effective_at) values (1, 1, 1, 7, '60', 'test7', 'ARREARS', 3, '2023-05-01');
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule, effective_at, ineffective_at) values (1, 1, 1, 8, '70', 'pb_effective_at_range_1', 'ARREARS', 1, '2023-01-01', '2023-07-01');
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule, effective_at) values (1, 1, 1, 9, '70', 'pb_effective_at_range_2', 'ARREARS', 1, '2023-07-01');
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule) values (1, 1, 1, 10, '80', 'dedup_test', 'ARREARS', 1);
INSERT INTO src.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule, version) values (1, 1, 1, 10, '80', 'dedup_test', 'ARREARS', 2, 1);

-- PRICEBOOK PRICES --
-- Pricebook 1
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 1, 1, 1, '0.25');
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 2, 2, 1, '1000', 'ADVANCED', 12);
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 3, 3, 1, '0.5');
-- Pricebook 2
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 4, 1, 2, '0.33');
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 5, 2, 2, '1000', 'ADVANCED', 12);
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 6, 3, 2, '0.66');
-- Pricebook 3
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 7, 1, 3, '0.25');
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 8, 2, 3, '100', 'ONE_TIME', 1);
-- Pricebook 4
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 9, 2, 4, '1000', 'ADVANCED', 12);
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, fixed_quantity) values (1, 1, 1, 10, 4, 4, '100', 2);
-- Pricebook 5
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, start_period, end_period) values (1, 1, 1, 11, 2, 5, '100', 0, 2);
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, start_period, end_period) values (1, 1, 1, 12, 2, 5, '999', 2, 12);
-- Pricebook 6
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 13, 1, 6, '0.33');
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 14, 2, 6, '1000', 'ADVANCED', 12);
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 15, 3, 6, '0.66');
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 16, 1, 7, '0.22');
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 17, 2, 7, '999', 'ADVANCED', 12);
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 18, 3, 7, '0.44');
-- Pricebook 7
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 19, 2, 8, '1000.00');
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 20, 2, 9, '588.99');
-- Pricebook 8
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price) values (1, 1, 1, 21, 1, 10, '0.00');
INSERT INTO src.list_prices (org_id, env_id, branch_id, id, product_uid, pricebook_uid, price, version) values (1, 1, 1, 21, 1, 10, '0.99', 1);

-- CONTRACT --
-- Normal contract
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 1, '88', '10', '10', '2023-01-01', '2024-01-01');
-- Slowly changing dimensions (contract ammendment) month end
INSERT INTO src.contracts (org_id, env_id, branch_id, id, durable_id, customer_id, pricebook_id, started_at, ended_at, effective_at, ineffective_at) values (1, 1, 1, 2, '99', '20', '10', '2023-01-01', '2024-01-01', '2023-01-01', '2023-07-01');
INSERT INTO src.contracts (org_id, env_id, branch_id, id, durable_id, customer_id, pricebook_id, started_at, ended_at, effective_at, ineffective_at) values (1, 1, 1, 3, '99', '20', '20', '2023-01-01', '2024-01-01', '2023-07-01', '2024-01-01');
-- Slowly changing dimensions (contract ammendment) inter-month
INSERT INTO src.contracts (org_id, env_id, branch_id, id, durable_id, customer_id, pricebook_id, prorate, started_at, ended_at, effective_at, ineffective_at) values (1, 1, 1, 4, '100', '30', '10', true, '2023-11-01', '2024-01-01', '2023-11-01', '2023-12-11');
INSERT INTO src.contracts (org_id, env_id, branch_id, id, durable_id, customer_id, pricebook_id, prorate, started_at, ended_at, effective_at, ineffective_at) values (1, 1, 1, 5, '100', '30', '20', true, '2023-11-01', '2024-01-01', '2023-12-11', '2024-01-01');
-- Test offset start and end, quarterly invoice schedules and one time charges
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2023-01-02', 6, '110', '40', '30', '2023-01-02', '2023-12-07');
-- Test proration works as intended, also test a fixed charge in arrears with an early stop
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, prorate, started_at, ended_at) values (1, 1, 1, '2023-01-02', 7, '120', '50', '40', true, '2023-01-02', '2023-11-07');
-- Test contract overrides
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 8, '130', '60', '10', '2023-01-01', '2024-01-01');
-- Test contract quantities and quantity overrides
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 9, '140', '70', '40', '2023-01-01', '2024-01-01');
-- Test scheduled prices
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 10, '150', '80', '50', '2023-01-01', '2024-01-01');
-- Test customer SCDs
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 11, '160', '90', '10', '2023-01-01', '2024-01-01');
-- Test pricebook SCDs
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 12, '170', '100', '60', '2023-01-01', '2024-01-01');
-- Test long dated contract
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2021-07-10', 13, '180', '110', '10', '2021-07-10', '2028-01-01');
-- Test ad hoc contract
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 14, '190', '120', '2023-01-01', '2024-01-01');
-- Test ad hoc contract price with specific dates
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 15, '200', '120', '2023-01-01', '2024-01-01');
-- Test ad hoc product even though there is a pricebook
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 16, '210', '120', '10', '2023-01-01', '2024-01-01');
-- Test void contract
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at, void, voided_at) values (1, 1, 1, '2023-01-01', 17, '220', '10', '10', '2023-01-01', '2024-01-01', true, '2023-01-01');
-- Test contract with effective dates on it and it's pricebook
INSERT INTO src.contracts (org_id, env_id, branch_id, id, durable_id, customer_id, pricebook_id, started_at, ended_at, effective_at, ineffective_at) values (1, 1, 1, 18, '230', '130', '70', '2023-01-01', '2024-01-01', '2023-01-01', '2023-07-01');
INSERT INTO src.contracts (org_id, env_id, branch_id, id, durable_id, customer_id, pricebook_id, started_at, ended_at, effective_at, ineffective_at) values (1, 1, 1, 19, '230', '130', '70', '2023-01-01', '2024-01-01', '2023-07-01', '2024-01-01');
-- duplicate contract
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 20, '87', 'fake', '10', '2023-01-01', '2024-01-01');
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at, version) values (1, 1, 1, '2023-01-01', 20, '87', 'fake', '10', '2023-01-01', '2024-02-01', 1);
-- null contract ended_at
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 21, '240', '140', '2023-01-01', NULL);
-- filter tests
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, started_at, ended_at) values (1, 1, 1, '2023-01-01', 22, '250', '150', '2023-01-01', '2024-01-01');
-- branch 2 contract
INSERT INTO src.contracts (org_id, env_id, branch_id, effective_at, id, durable_id, customer_id, pricebook_id, started_at, ended_at) values (1, 1, 2, '2023-01-01', 23, '260', '160', '10', '2023-01-01', '2024-01-01');

-- CONTRACT PRICES --
-- Contract 8
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, list_price_uid, contract_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 1, 2, 8, '12345', 'ADVANCED', 4);
-- Contract 9
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, list_price_uid, contract_uid, fixed_quantity) values (1, 1, 1, 2, 9, 9, 3);
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, list_price_uid, contract_uid, invoice_schedule, fixed_quantity) values (1, 1, 1, 3, 10, 9, 1, '0.95');
-- Contract 13
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, list_price_uid, contract_uid, invoice_schedule) values (1, 1, 1, 4, 2, 13, 7);
-- Contract 14
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, contract_uid, product_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 5, 14, 4, '55.34', 'ADVANCED', 3);
-- Contract 15
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, contract_uid, product_uid, price, invoice_delivery, invoice_schedule, prorate, started_at, ended_at) values (1, 1, 1, 6, 15, 4, '-1000.00', 'ADVANCED', 12, true, '2023-06-01', '2024-01-01');
-- Contract 15
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, contract_uid, product_uid, price, invoice_delivery, invoice_schedule, started_at, ended_at) values (1, 1, 1, 7, 16, 4, '-100.00', 'ADVANCED', 12, '2023-06-01', '2024-01-01');
-- Contract 20
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, contract_uid, product_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 8, 20, 1, '0.01', 'ARREARS', 1);
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, contract_uid, product_uid, price, invoice_delivery, invoice_schedule, version) values (1, 1, 1, 8, 20, 1, '0.02', 'ARREARS', 1, 1);
-- Contract 21
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, contract_uid, product_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 9, 21, 3, '0.01', 'ARREARS', 12);
-- Contract 22
INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, contract_uid, product_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 10, 22, 6, '1.00', 'ARREARS', 1);