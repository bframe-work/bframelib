import subprocess
import time
import sqlite3
from typing import NamedTuple
import pytest
import duckdb
from pathlib import Path
from bframelib import Client, Source, SCHEMA_SQL
from utils import standard_duckdb_client

class SourceClient(NamedTuple):
    client: Client
    args: Client.config

@pytest.fixture(scope="session")
def duckdb_client():
    c, args = standard_duckdb_client()
    yield SourceClient(c, args)
    c.con.close()

@pytest.fixture(scope="session")
def sqlite_client():
    # DuckDB does not properly transfer the typing to SQLite when creating tables from a duckdb connection. Specifically
    # this leads to timestamp columns being created as a text type. In order to circumvent this the schema is directly created in
    # SQLite and the types are specifically set.
    sqlite_db_path = 'tests/sqlite/test.db'
    con = sqlite3.connect(sqlite_db_path)

    cur = con.cursor()
    cur.executescript(SCHEMA_SQL)

    config = {
        'org_id': 1,
        'env_id': 1,
        'branch_id': 1,
        'system_dt': '2025-12-31',
        'rating_range': ['1900-01-01', '2200-01-01'],
        'contract_ids': [],
        'customer_ids': [],
        'product_uids': [],
        'pricebook_ids': [],
        'read_mode': 'VIRTUAL'
    }

    core_source_connect = f"""
        ATTACH '{sqlite_db_path}' AS src (TYPE SQLITE);
    """

    # When accessing SQLite tables DuckDB is conservative in it's typing. This leads to all integers being coerced into BIGINTs.
    # Amongst other coersion which can be read about here: https://duckdb.org/docs/extensions/sqlite.html#data-types
    # This causes errors within bframe, so we must cast necessary BIGINTs into INTs. This primarily occurs when we use the
    # to_months(INTEGER) and to_days(INTEGER) functions.
    sources = [Source('core', core_source_connect, False)]
    connection = duckdb.connect()
    c = Client(config, sources, connection)
    seed = Path('./tests/fixtures/1_seed.sql').read_text()
    c.execute(seed)
    yield SourceClient(c, config)
    Path(sqlite_db_path).unlink(True)

@pytest.fixture(scope="session")
def postgres_client():
    subprocess.run("docker compose -f ./tests/postgres/docker-compose.yml up -d", shell=True)
    time.sleep(1)  # Wait for services to start
    config = {
        'org_id': 1,
        'env_id': 1,
        'branch_id': 1,
        'system_dt': '2025-12-31',
        'rating_range': ['1900-01-01', '2200-01-01'],
        'contract_ids': [],
        'customer_ids': [],
        'product_uids': [],
        'pricebook_ids': [],
        'read_mode': 'VIRTUAL'
    }

    core_source_connect = """
        ATTACH 'postgres://first:password@localhost:5434/dev_db' AS src (TYPE POSTGRES);
        SET pg_experimental_filter_pushdown = true;
    """

    sources = [Source('core', core_source_connect, True)]
    connection = duckdb.connect()

    pg_client_online = False
    attempts = 0
    while(not pg_client_online and attempts < 3):
        try:
            c = Client(config, sources, connection)        
        except Exception:
            attempts = attempts + 1
            time.sleep(1)


    
    seed = Path('./tests/fixtures/1_seed.sql').read_text()
    c.execute(seed)
    yield SourceClient(c, config)
    subprocess.run("docker compose -f ./tests/postgres/docker-compose.yml down", shell=True)

@pytest.fixture(autouse=True, params=['duckdb', 'postgres', 'sqlite'])
def client(request: pytest.FixtureRequest, duckdb_client: SourceClient, postgres_client: SourceClient, sqlite_client: SourceClient):
    if (request.param == 'duckdb'):
        c, a = duckdb_client
    elif (request.param == 'postgres'):
        c, a = postgres_client
    elif (request.param == 'sqlite'):
        c, a = sqlite_client

    # NOTE: Transactions can rollback ATTACH / DETACH statements. But they do not rollback USE statements.
    # If a USE statement is specified and the database associated with it is DETACHED. A binder error will
    # be thrown.
    c.execute("BEGIN TRANSACTION;")
    yield c
    c.execute("ROLLBACK;")
    c.set_config(a)
    c.set_source(Source('branch', '', False))
    c.set_source(Source('events', '', False))