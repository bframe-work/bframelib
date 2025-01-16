import subprocess
import time
import pytest
import duckdb
from pathlib import Path
from bframelib import Client, Source
from utils import standard_duckdb_client

@pytest.fixture(scope="session")
def duckdb_client():
    c, args = standard_duckdb_client()
    yield (c, args)
    c.con.close()

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
    }

    core_source_connect = """
        ATTACH 'postgres://first:password@localhost:5434/dev_db' AS src (TYPE POSTGRES);
        SET pg_experimental_filter_pushdown = true;
    """

    sources = [Source('core', core_source_connect, True)]
    connection = duckdb.connect()
    c = Client(config, sources, connection)
    seed = Path('./tests/fixtures/1_seed.sql').read_text()
    c.execute(seed)
    yield (c, config)
    subprocess.run("docker compose -f tests/postgres/docker-compose.yml down", shell=True)

@pytest.fixture(autouse=True, params=['duckdb', 'postgres'])
def client(request: pytest.FixtureRequest, duckdb_client: tuple[Client, dict[str, any]], postgres_client: tuple[Client, dict[str, any]]):
    if (request.param == 'duckdb'):
        c = duckdb_client[0]
        a = duckdb_client[1]
    elif (request.param == 'postgres'):
        c = postgres_client[0]
        a = postgres_client[1]

    # NOTE: Transactions can rollback ATTACH / DETACH statements. But they do not rollback USE statements.
    # If a USE statement is specified and the database associated with it is DETACHED. A binder error will
    # be thrown.
    c.execute("BEGIN TRANSACTION;")
    yield c
    c.execute("ROLLBACK;")
    c.set_config(a)
    c.set_source(Source('branch', '', False))
    c.set_source(Source('events', '', False))