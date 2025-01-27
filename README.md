# bframe

[bframe](https://bframe.work) is a library to generate, view and diff invoices locally.

Key technical features:
* **Pure SQL** - bframe's business logic is entirely written in customizable SQL views.
* **No infrastructure** - The library is fully in process with no hosting or docker required.
* **Choose your source** - Utilizing [duckdb](https://duckdb.org/) extensions, many sources of data are supported (Postgres, S3 compatible, etc).

Key billing use cases supported:
* **Complex pricing and packaging** - Supports pricing usage, subscriptions or custom [user defined views](https://bframe.work/features/user_defined_views.html).
* **Branching** - Create git-like [branches](https://bframe.work/features/branching.html) to test isolated changes using production data and then compare the results to the main branch
* **Edits and amendments** - Easily make [edits](https://bframe.work/features/edits.html) or [amendments](https://bframe.work/features/amendments.html) to pricing and packaging.
* **Time travel** - Rewind the [system time](https://bframe.work/features/system_time.html) of the business model to audit, debug and reconcile historical changes.

## Installation
Open a terminal and run (Requires Python 3.9+):

```bash
pip install bframelib
```

## Usage
`bframelib` is a client that sits on top of a duckdb connection. Within the client is an interpreter that injects SQL based on the specified bframe views that are referenced (e.g. ``bframe.invoices``). [Additional options](https://bframe.work/interface_api/variables.html) are set within the library config and can control branching, system time and more.

Below is a short example to show the most direct usage of `bframelib`.

```python
from bframelib import Client
config = {
    "org_id": 1,
    "env_id": 1,
    "branch_id": 1,
    "rating_range": ['2025-01-01', '2026-01-01']
}

# The client will create a duckdb connection if it is not provided
bf = Client(config)

# Set up your source data (bframe uses duckdb if a source is not specified)
bf.execute("""
    -- Set up the tenant
    INSERT INTO src.organizations (id, name) values (1, 'Your business');
    INSERT INTO src.environments (id, org_id, name) values (1, 1, 'PROD');
    INSERT INTO src.branches (id, org_id, env_id, name) values (1, 1, 1, 'main');

    -- Create customer
    INSERT INTO src.customers (org_id, env_id, branch_id, id, durable_id, name) values (1, 1, 1, 1, 'abc', 'Customer name');

    -- Create product
    INSERT INTO src.products (org_id, env_id, branch_id, id, name, ptype) values (1, 1, 1, 1, 'Item', 'FIXED');

    -- Create contract and prices
    INSERT INTO src.contracts (org_id, env_id, branch_id,  id, durable_id, customer_id, started_at, ended_at, effective_at) values (1, 1, 1, 1, 'abc_contract', 'abc', '2025-01-01', '2026-01-01', '2025-01-01');
    INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, product_uid, contract_uid, price, invoice_delivery, invoice_schedule) values (1, 1, 1, 1, 1, 1, '10.00', 'ARREARS', 1);
""")

# Generate invoices
res = bf.execute("""
    SELECT 
        contract_id,
        invoice_delivery,
        started_at,
        ended_at,
        status,
        total
    FROM bframe.invoices
    ORDER BY ended_at
""")

print(res.fetch_df().to_string())
#      contract_id invoice_delivery started_at   ended_at status  total
# 0   abc_contract          ARREARS 2025-01-01 2025-02-01  DRAFT   10.0
# 1   abc_contract          ARREARS 2025-02-01 2025-03-01  DRAFT   10.0
# 2   abc_contract          ARREARS 2025-03-01 2025-04-01  DRAFT   10.0
# 3   abc_contract          ARREARS 2025-04-01 2025-05-01  DRAFT   10.0
# 4   abc_contract          ARREARS 2025-05-01 2025-06-01  DRAFT   10.0
# 5   abc_contract          ARREARS 2025-06-01 2025-07-01  DRAFT   10.0
# 6   abc_contract          ARREARS 2025-07-01 2025-08-01  DRAFT   10.0
# 7   abc_contract          ARREARS 2025-08-01 2025-09-01  DRAFT   10.0
# 8   abc_contract          ARREARS 2025-09-01 2025-10-01  DRAFT   10.0
# 9   abc_contract          ARREARS 2025-10-01 2025-11-01  DRAFT   10.0
# 10  abc_contract          ARREARS 2025-11-01 2025-12-01  DRAFT   10.0
# 11  abc_contract          ARREARS 2025-12-01 2026-01-01  DRAFT   10.0
    
```

## API
The `bframelib` is composed of a `Client` and `Interpreter`. The `Client` is the primary interface for library users and the `Interpreter` is the engine that powers the business logic. Both are exposed through the library but only more advanced use cases will utilize the interpreter directly.

### `Source`
A named tuple that represents a source.

#### `__init__(src_type, connect_sql, init_schema)`
The initialization of the named tuple.

**Parameters:**
* `src_type` - An enum string to represent the source that is being attach. Possible values include ('core', 'branch', 'events').
* `connect_sql` - A SQL string that is executed to assign the specified source. The function expects an `ATTACH` statement using the [duckdb SQL dialect](https://duckdb.org/docs/sql/statements/attach.html). An example of what this could look like: `"ATTACH ':memory:' AS src;"`
* `init_schema` - A boolean with a default value of `False`. If set to `True` the source database attached will have the bframe schema executed on it.

### `Client`
A class that represents the bframe library interface for a duckdb connection.

#### `config`
A property to view the current configuration options.

**Returns:**
A dictionary of the library configurations that have been set.

#### `__init__(config, sources, con)`
The initialization of the `Client` class.

**Parameters:**
* `config` - A dictionary containing configuration options. Detailed option definitions can be found [here](https://bframe.work/interface_api/variables.html).
* `sources` - A list of `Source` tuples to be set. If no list is passed a default core source will be passed.
* `con` - A pre-initialized [`duckdb connection`](https://duckdb.org/docs/api/python/reference/#duckdb.DuckDBPyConnection). If this is not present a new connection will be created.

#### `set_config(config_updates)`
A function to set configuration options.

**Parameters:**
* `config_updates` - A dictionary containing one or more updates to the library config. Detailed option definitions can be found [here](https://bframe.work/interface_api/variables.html).

**Returns:**
Void

#### `execute(query)`
A function to interpret bframe SQL and execute it on the given duckdb connection.

**Parameters:**
* `query` - A string containing one or more SQL statements.

**Returns:**
A [`DuckDBPyConnection`](https://duckdb.org/docs/api/python/reference/#duckdb.DuckDBPyConnection) that holds the results of the executed SQL statement.

#### `get_price_span_date_range(product_types)`
A function to pull the maximum time range of the currently configured invoices. This can enable effective use of event source partitions (e.g. only sourcing events that are needed for invoice generation).

**Parameters:**
* `product_types` - A tuple that contains one or more product types

**Returns:**
A tuple with the first element representing the minimum start date of all invoices and the second element representing maximum end date of all invoices.

#### `set_source(Source)`
A function to set the `src` database bframe pulls data from. It will detach the existing `src` during execution.

**Parameters:**
* `connect_sql` - A SQL string that is executed to assign the `src` database. The function expects an `ATTACH` statement using the [duckdb SQL dialect](https://duckdb.org/docs/sql/statements/attach.html). An example of what this could look like: `"ATTACH ':memory:' AS src;"`
* `init_schema` - A boolean with a default value of `False`. If set to `True` the `src` database attached will have the bframe schema executed on it.

**Returns:**
Void

#### `interpreter.add_table_template(name, template)`
A function on the stored `Interpreter` class that sets a [user defined view](https://bframe.work/features/user_defined_view.html).

**Parameters:**
* `name` - A string that represents the view name (e.g. `bframe.YOUR_NAME_HERE`)
* `template` - SQL that represents the view itself

**Returns:**
Void

## Resources

[Documentation](https://bframe.work)

[Github repository](https://github.com/bframe-work/bframelib)
