import duckdb
from pathlib import Path
from bframelib import Client, DEFAULT_SOURCES

# Initially I looked into how to unpack dictionaries a bit more cleanly, but the sqlite3 library doesn't have anything to solve this case
# The recommendation is to use the sqlite string argument interpolation, and not string interpolation due to risk of sql injection
# since these are just tests, we think it's fine to just do string interpolation during INSERTs. This significantly cleans up our code by
# doing things with string interpolation and the tradeoff is we end up using this in production later on. I'm not too worried about that since
# since we don't plan on using sqlite in production in the first place.
def field_value_tuple(obj_dict):
    fields, values = zip(*obj_dict.items())
    str_values = []
    for value in values:
        if value == None:
            str_values.append('NULL')
        else:
            str_values.append(str(value))
    return (str(fields).replace("'", ""), tuple(str_values))


def standard_duckdb_client(config: dict = {}, sources = DEFAULT_SOURCES, connection = None):
    config['org_id'] = config.get('org_id', 1)
    config['env_id'] = config.get('env_id', 1)
    config['branch_id'] = config.get('branch_id', 1)
    config['system_dt'] = config.get('system_dt', '2025-12-31')
    config['rating_range'] = config.get('rating_range', ['1900-01-01', '2200-01-01'])
    config['stored_rating_range'] = config.get('stored_rating_range', ['1900-01-01', '2200-01-01'])
    config['contract_ids'] = config.get('contract_ids', [])
    config['customer_ids'] = config.get('customer_ids', [])
    config['product_uids'] = config.get('product_uids', [])
    config['pricebook_ids'] = config.get('pricebook_ids', [])
    config['read_mode'] = config.get('read_mode', 'VIRTUAL')

    
    connection = duckdb.connect()
    c = Client(config, sources, connection)
    seed = Path('./tests/fixtures/1_seed.sql').read_text()
    c.execute(seed)
    return (c, config)