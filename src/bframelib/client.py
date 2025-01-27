import datetime
import duckdb
from typing import NamedTuple
from pathlib import Path
from . import interpreter, PATH

REQUIRED_FIELDS = ['org_id', 'env_id', 'branch_id']

class Source(NamedTuple):
    src_type: str
    connect_sql: str
    init_schema: bool

DEFAULT_SOURCES = [
    Source('core', "ATTACH ':memory:' AS src;", True),
]


class Client():
    branch_source_exists: bool = False
    events_source_exists: bool = False
    # Manually set to point local events at the events source
    events_source_local: bool = False

    def __init__(
            self,
            config: dict,
            sources: list[Source] | None = DEFAULT_SOURCES,
            con: duckdb.DuckDBPyConnection | None = None,
        ):

        if (con == None):
            self.con = duckdb.connect()
        else:
            self.con = con

        # TODO Would be better typed
        self._config = {
            'org_id': None,
            'env_id': None,
            'branch_id': None,
            'system_dt': (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
            'rating_as_of_dt': datetime.datetime.now().isoformat(),
            'rating_range': [],
            'contract_ids': [],
            'customer_ids': [],
            'product_uids': [],
            'dedup_branch_events': False
        }
        self.set_config(config)
        
        for source in sources:
            self.set_source(source)

        # Validate required fields
        missing_fields = {field: self._config[field] for field in REQUIRED_FIELDS if self._config[field] is None}
        if missing_fields:
            raise Exception(f'Missing one of the required configuration fields: {missing_fields}')

        self.interpreter = interpreter.Interpreter()

    @property
    def config(self):
        return self._config.copy()
    
    def set_source(self, source: Source):
        src_type, connect_sql, init_schema = source

        if src_type == 'core':
            self.con.execute('USE memory; DETACH DATABASE IF EXISTS src;')

            if connect_sql:
                self.con.execute(connect_sql)
            else:
                self.con.execute("ATTACH ':memory:' AS src;")

            if init_schema:
                schema = Path(f'{PATH}/bootstrap_sql/0_init.sql').read_text()
                self.con.execute('USE src;')
                self.con.execute(schema)
        elif src_type == 'branch':
            self.con.execute('DETACH DATABASE IF EXISTS brch;')

            # The interpreter will use the src database in the case there is no brch
            if connect_sql:
                self.con.execute(connect_sql)

                if init_schema:
                    schema = Path(f'{PATH}/bootstrap_sql/0_init.sql').read_text()
                    self.con.execute('USE brch;')
                    self.con.execute(schema)
                    self.con.execute('USE memory;')
                
                self.branch_source_exists = True
            else:
                self.branch_source_exists = False
        elif src_type == 'events':
            self.con.execute('USE memory; DETACH DATABASE IF EXISTS evt;')

            # The interpreter will use the src database in the case there is no evt
            if connect_sql:
                self.con.execute(connect_sql)
                self.events_source_exists = True
            else:
                self.events_source_exists = False
    
    def set_config(self, config_updates: dict):
        # Handle unknown fields
        for key, _ in config_updates.items():
            if key not in self._config:
                raise Exception(f'Unknown fields can not be set: {key}')
        
        # Update configuration with new values, maintaining defaults
        for key, _ in self._config.items():
            new_value = config_updates.get(key)
            if key in config_updates:
                if key in REQUIRED_FIELDS and new_value == None:
                    raise Exception(f'Required field can not be set to None')

                if key in ('branch_source_connect', 'core_source_connect'):
                    self.con.execute(new_value)

                self._config[key] = new_value

    def execute(self, query):
        variables = self.config
        variables['branch_source_exists'] = self.branch_source_exists
        variables['events_source_exists'] = self.events_source_exists
        variables['events_source_local'] = self.events_source_local

        resolved_query = self.interpreter.exec(variables, query)
        return self.con.execute(resolved_query)

    def get_price_span_date_range(self, product_types: tuple): 
        # Takes a list of product types to include (EVENT, FIXED)
        return self.execute(f"""
            SELECT date_trunc('month', MIN(started_at))::timestamp, date_trunc('month', MAX(ended_at))::timestamp
            FROM bframe.price_spans
            WHERE product_type IN {str(product_types)}
        """).fetchone()

