CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS environments (
    id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    org_id INTEGER,
    UNIQUE (id, org_id)
);

CREATE TABLE IF NOT EXISTS branches (
    id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    org_id INTEGER,
    env_id INTEGER,
    UNIQUE (id, org_id, env_id)
);

CREATE TABLE IF NOT EXISTS customers (
    id BIGINT NOT NULL,
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    durable_id TEXT NOT NULL,
    ingest_aliases JSON NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_at TIMESTAMP DEFAULT '1900-01-01T00:00:00+00:00',
    ineffective_at TIMESTAMP DEFAULT '2500-01-01T00:00:00+00:00',
    name TEXT NOT NULL,
    archived_at TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version, org_id, env_id)
);

CREATE TABLE IF NOT EXISTS events (
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    transaction_id TEXT NOT NULL,
    customer_id TEXT,
    customer_alias TEXT,
    properties JSON,
    metered_at TIMESTAMP NOT NULL,
    received_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id BIGINT NOT NULL,
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    ptype TEXT NOT NULL,
    event_name TEXT,
    filters JSON,
    agg_property TEXT,
    archived_at TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version, org_id, env_id),
    CHECK (ptype <> 'FIXED' OR (ptype = 'FIXED' AND filters IS NULL AND agg_property IS NULL AND event_name IS NULL))
);

CREATE TABLE IF NOT EXISTS pricebooks (
    id BIGINT NOT NULL,
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    durable_id TEXT NOT NULL,
    prorate BOOLEAN,
    name TEXT NOT NULL,
    invoice_delivery TEXT NOT NULL,
    invoice_schedule INTEGER NOT NULL,
    billing_target TEXT,
    effective_at TIMESTAMP,
    ineffective_at TIMESTAMP,
    archived_at TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version, org_id, env_id)
);

CREATE TABLE IF NOT EXISTS contracts (
    id BIGINT NOT NULL,
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    durable_id TEXT NOT NULL,
    prorate BOOLEAN,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    customer_id TEXT NOT NULL,
    pricebook_id TEXT,
    void BOOLEAN DEFAULT FALSE,
    voided_at TIMESTAMP,
    archived_at TIMESTAMP,
    effective_at TIMESTAMP NOT NULL,
    ineffective_at TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version, org_id, env_id),
    UNIQUE (durable_id, effective_at, version),
    CHECK ((void AND voided_at IS NOT NULL) OR (NOT void AND voided_at IS NULL)),
    CHECK (started_at < ended_at),
    CHECK (effective_at BETWEEN started_at AND ended_at),
    CHECK (ineffective_at BETWEEN started_at AND ended_at),
    CHECK (effective_at <= ineffective_at)
);

CREATE TABLE IF NOT EXISTS list_prices (
    id BIGINT NOT NULL,
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    price TEXT NOT NULL,
    invoice_delivery TEXT,
    invoice_schedule INTEGER,
    start_period INTEGER,
    end_period INTEGER,
    fixed_quantity DECIMAL,
    prorate BOOLEAN,
    product_uid INTEGER,
    pricebook_uid INTEGER,
    pricing_metadata JSON,
    version INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version, org_id, env_id)
);

CREATE TABLE IF NOT EXISTS contract_prices (
    id BIGINT NOT NULL,
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    price TEXT,
    invoice_delivery TEXT,
    invoice_schedule INTEGER,
    start_period INTEGER,
    end_period INTEGER,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    fixed_quantity DECIMAL,
    prorate BOOLEAN,
    product_uid INTEGER,
    list_price_uid INTEGER,
    contract_uid INTEGER,
    pricing_metadata JSON,
    version INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version, org_id, env_id),
    CHECK (COALESCE(list_price_uid, product_uid) IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS dates (
    month_start TIMESTAMP NOT NULL,
    month_end TIMESTAMP NOT NULL,
    UNIQUE (month_start, month_end)
);

CREATE TABLE IF NOT EXISTS rated_events (
    id TEXT PRIMARY KEY,
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    transaction_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    customer_alias TEXT,
    properties JSON NOT NULL,
    metered_at TIMESTAMP NOT NULL,
    received_at TIMESTAMP NOT NULL,
    list_price_uid INTEGER,
    contract_price_uid INTEGER,
    product_uid INTEGER NOT NULL,
    product_type TEXT NOT NULL,
    status TEXT NOT NULL,
    price TEXT NOT NULL,
    quantity DECIMAL NOT NULL,
    amount DECIMAL NOT NULL,
    contract_id TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP NOT NULL,
    effective_at TIMESTAMP NOT NULL,
    ineffective_at TIMESTAMP NOT NULL,
    invoice_delivery TEXT NOT NULL,
    CHECK (COALESCE(list_price_uid, contract_price_uid) IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS line_items (
    id TEXT PRIMARY KEY,
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    list_price_uid INTEGER,
    contract_price_uid INTEGER,
    product_uid INTEGER NOT NULL,
    contract_id TEXT NOT NULL,
    invoice_delivery TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP NOT NULL,
    effective_at TIMESTAMP NOT NULL,
    ineffective_at TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    quantity DECIMAL NOT NULL,
    amount DECIMAL NOT NULL,
    CHECK (COALESCE(list_price_uid, contract_price_uid) IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY,
    org_id INTEGER NOT NULL,
    env_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    contract_id TEXT NOT NULL,
    invoice_delivery TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    total DECIMAL NOT NULL
);

CREATE TABLE IF NOT EXISTS price_spans (
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP NOT NULL,
    effective_at TIMESTAMP NOT NULL,
    ineffective_at TIMESTAMP NOT NULL,
    proration_start TIMESTAMP NOT NULL,
    proration_end TIMESTAMP NOT NULL,
    price TEXT NOT NULL,
    pricing_metadata JSON,
    fixed_quantity DECIMAL,
    product_type TEXT NOT NULL,
    invoice_delivery TEXT NOT NULL,
    prorate BOOLEAN,
    list_price_uid INTEGER,
    contract_price_uid INTEGER,
    product_uid INTEGER NOT NULL,
    pricebook_id TEXT,
    contract_id TEXT NOT NULL,
    contract_uid BIGINT NOT NULL,
    customer_id TEXT NOT NULL,
    CHECK (started_at < ended_at),
    CHECK (effective_at <= ineffective_at),
    CHECK (proration_start <= proration_end)
);

CREATE TABLE IF NOT EXISTS prices (
    list_price_uid INTEGER,
    contract_price_uid INTEGER,
    price TEXT NOT NULL,
    invoice_delivery TEXT NOT NULL,
    invoice_schedule INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP NOT NULL,
    effective_at TIMESTAMP,
    ineffective_at TIMESTAMP,
    fixed_quantity DECIMAL,
    product_type TEXT NOT NULL,
    product_uid INTEGER NOT NULL,
    pricebook_uid INTEGER,
    contract_uid BIGINT NOT NULL,
    prorate BOOLEAN,
    pricing_metadata JSON,
    CHECK (COALESCE(list_price_uid, contract_price_uid) IS NOT NULL),
    CHECK (started_at < ended_at),
    CHECK (effective_at IS NULL OR ineffective_at IS NULL OR effective_at <= ineffective_at)
);

CREATE TABLE IF NOT EXISTS processed_events (
    transaction_id TEXT NOT NULL,
    customer_id TEXT,
    customer_alias TEXT,
    properties JSON,
    metered_at TIMESTAMP NOT NULL,
    received_at TIMESTAMP NOT NULL,
    resolved_customer_id TEXT
);

CREATE TABLE IF NOT EXISTS matched_events (
    transaction_id TEXT NOT NULL,
    customer_id TEXT,
    customer_alias TEXT,
    properties JSON,
    metered_at TIMESTAMP NOT NULL,
    received_at TIMESTAMP NOT NULL,
    quantity DECIMAL NOT NULL,
    product_uid INTEGER NOT NULL,
    product_type TEXT NOT NULL
);


-- DATES --
-- source: https://docs.google.com/spreadsheets/d/1qGBkNFwhN9CR_x_esnT985EFYVksIvNLxTedD77udG8/edit#gid=0
INSERT INTO dates (month_start, month_end) VALUES ('2016-01-01', '2016-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2016-02-01', '2016-02-29');
INSERT INTO dates (month_start, month_end) VALUES ('2016-03-01', '2016-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2016-04-01', '2016-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2016-05-01', '2016-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2016-06-01', '2016-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2016-07-01', '2016-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2016-08-01', '2016-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2016-09-01', '2016-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2016-10-01', '2016-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2016-11-01', '2016-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2016-12-01', '2016-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2017-01-01', '2017-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2017-02-01', '2017-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2017-03-01', '2017-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2017-04-01', '2017-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2017-05-01', '2017-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2017-06-01', '2017-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2017-07-01', '2017-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2017-08-01', '2017-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2017-09-01', '2017-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2017-10-01', '2017-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2017-11-01', '2017-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2017-12-01', '2017-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2018-01-01', '2018-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2018-02-01', '2018-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2018-03-01', '2018-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2018-04-01', '2018-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2018-05-01', '2018-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2018-06-01', '2018-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2018-07-01', '2018-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2018-08-01', '2018-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2018-09-01', '2018-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2018-10-01', '2018-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2018-11-01', '2018-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2018-12-01', '2018-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2019-01-01', '2019-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2019-02-01', '2019-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2019-03-01', '2019-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2019-04-01', '2019-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2019-05-01', '2019-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2019-06-01', '2019-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2019-07-01', '2019-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2019-08-01', '2019-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2019-09-01', '2019-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2019-10-01', '2019-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2019-11-01', '2019-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2019-12-01', '2019-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2020-01-01', '2020-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2020-02-01', '2020-02-29');
INSERT INTO dates (month_start, month_end) VALUES ('2020-03-01', '2020-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2020-04-01', '2020-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2020-05-01', '2020-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2020-06-01', '2020-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2020-07-01', '2020-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2020-08-01', '2020-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2020-09-01', '2020-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2020-10-01', '2020-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2020-11-01', '2020-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2020-12-01', '2020-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2021-01-01', '2021-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2021-02-01', '2021-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2021-03-01', '2021-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2021-04-01', '2021-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2021-05-01', '2021-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2021-06-01', '2021-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2021-07-01', '2021-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2021-08-01', '2021-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2021-09-01', '2021-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2021-10-01', '2021-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2021-11-01', '2021-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2021-12-01', '2021-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2022-01-01', '2022-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2022-02-01', '2022-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2022-03-01', '2022-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2022-04-01', '2022-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2022-05-01', '2022-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2022-06-01', '2022-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2022-07-01', '2022-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2022-08-01', '2022-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2022-09-01', '2022-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2022-10-01', '2022-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2022-11-01', '2022-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2022-12-01', '2022-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2023-01-01', '2023-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2023-02-01', '2023-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2023-03-01', '2023-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2023-04-01', '2023-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2023-05-01', '2023-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2023-06-01', '2023-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2023-07-01', '2023-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2023-08-01', '2023-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2023-09-01', '2023-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2023-10-01', '2023-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2023-11-01', '2023-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2023-12-01', '2023-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2024-01-01', '2024-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2024-02-01', '2024-02-29');
INSERT INTO dates (month_start, month_end) VALUES ('2024-03-01', '2024-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2024-04-01', '2024-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2024-05-01', '2024-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2024-06-01', '2024-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2024-07-01', '2024-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2024-08-01', '2024-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2024-09-01', '2024-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2024-10-01', '2024-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2024-11-01', '2024-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2024-12-01', '2024-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2025-01-01', '2025-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2025-02-01', '2025-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2025-03-01', '2025-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2025-04-01', '2025-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2025-05-01', '2025-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2025-06-01', '2025-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2025-07-01', '2025-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2025-08-01', '2025-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2025-09-01', '2025-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2025-10-01', '2025-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2025-11-01', '2025-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2025-12-01', '2025-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2026-01-01', '2026-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2026-02-01', '2026-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2026-03-01', '2026-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2026-04-01', '2026-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2026-05-01', '2026-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2026-06-01', '2026-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2026-07-01', '2026-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2026-08-01', '2026-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2026-09-01', '2026-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2026-10-01', '2026-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2026-11-01', '2026-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2026-12-01', '2026-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2027-01-01', '2027-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2027-02-01', '2027-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2027-03-01', '2027-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2027-04-01', '2027-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2027-05-01', '2027-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2027-06-01', '2027-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2027-07-01', '2027-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2027-08-01', '2027-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2027-09-01', '2027-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2027-10-01', '2027-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2027-11-01', '2027-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2027-12-01', '2027-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2028-01-01', '2028-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2028-02-01', '2028-02-29');
INSERT INTO dates (month_start, month_end) VALUES ('2028-03-01', '2028-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2028-04-01', '2028-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2028-05-01', '2028-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2028-06-01', '2028-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2028-07-01', '2028-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2028-08-01', '2028-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2028-09-01', '2028-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2028-10-01', '2028-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2028-11-01', '2028-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2028-12-01', '2028-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2029-01-01', '2029-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2029-02-01', '2029-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2029-03-01', '2029-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2029-04-01', '2029-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2029-05-01', '2029-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2029-06-01', '2029-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2029-07-01', '2029-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2029-08-01', '2029-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2029-09-01', '2029-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2029-10-01', '2029-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2029-11-01', '2029-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2029-12-01', '2029-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2030-01-01', '2030-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2030-02-01', '2030-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2030-03-01', '2030-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2030-04-01', '2030-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2030-05-01', '2030-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2030-06-01', '2030-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2030-07-01', '2030-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2030-08-01', '2030-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2030-09-01', '2030-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2030-10-01', '2030-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2030-11-01', '2030-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2030-12-01', '2030-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2031-01-01', '2031-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2031-02-01', '2031-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2031-03-01', '2031-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2031-04-01', '2031-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2031-05-01', '2031-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2031-06-01', '2031-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2031-07-01', '2031-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2031-08-01', '2031-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2031-09-01', '2031-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2031-10-01', '2031-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2031-11-01', '2031-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2031-12-01', '2031-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2032-01-01', '2032-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2032-02-01', '2032-02-29');
INSERT INTO dates (month_start, month_end) VALUES ('2032-03-01', '2032-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2032-04-01', '2032-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2032-05-01', '2032-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2032-06-01', '2032-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2032-07-01', '2032-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2032-08-01', '2032-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2032-09-01', '2032-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2032-10-01', '2032-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2032-11-01', '2032-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2032-12-01', '2032-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2033-01-01', '2033-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2033-02-01', '2033-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2033-03-01', '2033-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2033-04-01', '2033-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2033-05-01', '2033-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2033-06-01', '2033-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2033-07-01', '2033-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2033-08-01', '2033-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2033-09-01', '2033-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2033-10-01', '2033-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2033-11-01', '2033-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2033-12-01', '2033-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2034-01-01', '2034-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2034-02-01', '2034-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2034-03-01', '2034-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2034-04-01', '2034-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2034-05-01', '2034-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2034-06-01', '2034-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2034-07-01', '2034-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2034-08-01', '2034-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2034-09-01', '2034-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2034-10-01', '2034-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2034-11-01', '2034-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2034-12-01', '2034-12-31');
INSERT INTO dates (month_start, month_end) VALUES ('2035-01-01', '2035-01-31');
INSERT INTO dates (month_start, month_end) VALUES ('2035-02-01', '2035-02-28');
INSERT INTO dates (month_start, month_end) VALUES ('2035-03-01', '2035-03-31');
INSERT INTO dates (month_start, month_end) VALUES ('2035-04-01', '2035-04-30');
INSERT INTO dates (month_start, month_end) VALUES ('2035-05-01', '2035-05-31');
INSERT INTO dates (month_start, month_end) VALUES ('2035-06-01', '2035-06-30');
INSERT INTO dates (month_start, month_end) VALUES ('2035-07-01', '2035-07-31');
INSERT INTO dates (month_start, month_end) VALUES ('2035-08-01', '2035-08-31');
INSERT INTO dates (month_start, month_end) VALUES ('2035-09-01', '2035-09-30');
INSERT INTO dates (month_start, month_end) VALUES ('2035-10-01', '2035-10-31');
INSERT INTO dates (month_start, month_end) VALUES ('2035-11-01', '2035-11-30');
INSERT INTO dates (month_start, month_end) VALUES ('2035-12-01', '2035-12-31');
