import subprocess
import time
import pytest
import duckdb
from pathlib import Path
from bframelib import Client

@pytest.fixture(scope="session")
def duckdb_client():
    args = {
        'org_id': 1,
        'env_id': 1,
        'branch_id': 1,
        'system_dt': '2025-12-31',
        'rating_range': ['1900-01-01', '2200-01-01'],
        'contract_ids': []
    }

    connection = duckdb.connect()
    c = Client(init_client=True, con=connection, **args)
    seed = Path('./tests/fixtures/1_seed.sql').read_text()
    c.execute(seed)
    yield (c, args)
    connection.close()

@pytest.fixture(scope="session")
def postgres_client():
    subprocess.run("docker compose -f ./tests/postgres/docker-compose.yml up -d", shell=True)
    time.sleep(1)  # Wait for services to start
    args = {
        'org_id': 1,
        'env_id': 1,
        'branch_id': 1,
        'system_dt': '2025-12-31',
        'rating_range': ['1900-01-01', '2200-01-01'],
        'contract_ids': [],
        'core_source_connect': """
            ATTACH 'postgres://first:password@localhost:5434/dev_db' AS src (TYPE POSTGRES);
            SET pg_experimental_filter_pushdown = true;
            USE src;
        """
    }

    connection = duckdb.connect()
    c = Client(init_client=True, con=connection, **args)
    seed = Path('./tests/fixtures/1_seed.sql').read_text()
    c.execute(seed)
    yield (c, args)
    subprocess.run("docker compose -f tests/postgres/docker-compose.yml down", shell=True)

@pytest.fixture(autouse=True, params=['duckdb', 'postgres'])
def client(request: pytest.FixtureRequest, duckdb_client: tuple[Client, dict[str, any]], postgres_client: tuple[Client, dict[str, any]]):
    if (request.param == 'duckdb'):
        c = duckdb_client[0]
        a = duckdb_client[1]
    elif (request.param == 'postgres'):
        c = postgres_client[0]
        a = postgres_client[1]

    c.execute("BEGIN TRANSACTION;")
    yield c
    c.execute("ROLLBACK;")
    c.set_config(a)