import datetime
import duckdb
from pathlib import Path
from . import interpreter, PATH

class Client():
    def __init__(self, init_client=False, con=None, **kwargs):
        self._config = {
            'org_id': None,
            'env_id': None,
            'branch_id': None,
            'system_dt': (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
            'rating_as_of_dt': datetime.datetime.now().isoformat(),
            'rating_range': [],
            'events_source': 'src.events',
            'core_source_connect': None,
            'core_destination_connect': None,
            'contract_ids': [],
            'dedup_branch_events': False
        }
        self.set_config(kwargs)

        if (con == None):
            self.con = duckdb.connect()
        else:
            self.con = con
        
        if (init_client):
            self.con.execute("SET TimeZone = 'UTC';")
            if self.config['core_source_connect'] == None:
                # Create a new database that will be in memory
                self.con.execute("ATTACH ':memory:' AS src; USE src;")
            else:
                self.con.execute(self.config['core_source_connect'])

            schema = Path(f'{PATH}/bootstrap_sql/0_init.sql').read_text()
            self.con.execute(schema)
        else:
            self.con.execute(self.config['core_source_connect'])
        
        self.interpreter = interpreter.Interpreter()

    @property
    def config(self):
        return self._config.copy()
    
    def set_config(self, config_updates: dict):
        # Handle unknown fields
        for key, _ in config_updates.items():
            if key not in self._config:
                raise Exception(f'Unknown fields can not be set: {key}')
        
        # Update configuration with new values, maintaining defaults
        for key, _ in self._config.items():
            if key in config_updates:
                self._config[key] = config_updates.get(key)

        # Validate required fields
        required_fields = ['org_id', 'env_id', 'branch_id']
        missing_fields = {field: self._config[field] for field in required_fields if self._config[field] is None}
        if missing_fields:
            raise Exception(f'Missing one of the required configuration fields: {missing_fields}')

    def execute(self, query):
        resolved_query = self.interpreter.exec(self._config, query)
        return self.con.execute(resolved_query)

    def get_price_span_date_range(self, product_types: tuple): 
        # Takes a list of product types to include (EVENT, FIXED)
        return self.execute(f"""
            SELECT date_trunc('month', MIN(started_at))::timestamp, date_trunc('month', MAX(ended_at))::timestamp
            FROM bframe.price_spans
            WHERE product_type IN {str(product_types)}
        """).fetchone()

