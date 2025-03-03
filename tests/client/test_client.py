from bframelib import Client, Source, DEFAULT_SOURCES
from utils import standard_duckdb_client

class TestBframeClient:
    def test_client_defaults(self):
        config = {
            'org_id': 1,
            'env_id': 1,
            'branch_id': 1
        }
        c = Client(config)
        
        assert c.config['system_dt'] != None
        assert c.config['rating_as_of_dt'] != None
        assert c.config['contract_ids'] == []
        assert c.config['rating_range'] == []
        assert c.config['dedup_branch_events'] == False
    
    def test_client_init(self):
        config = {
            'org_id': 1,
            'env_id': 1,
            'branch_id': 1,
            'rating_range': ['1900-01-01', '2200-01-01'],
            'contract_ids': []
        }
        c = Client(config)
        
        res = c.execute('SELECT * FROM bframe.customers')

        assert res.fetchone() == None
    
    def test_client_init_missing_required_fields(self):
        config = {
            'env_id': 1,
            'branch_id': 1,
        }
        
        try:
            Client(config)
        except:
            assert True
        else:
            assert False

        config = {
            'org_id': 1,
            'branch_id': 1,
        }
        

        try:
            Client(config)
        except:
            assert True
        else:
            assert False
        
        config = {
            'org_id': 1,
            'env_id': 1,
        }
        

        try:
            Client(config)
        except:
            assert True
        else:
            assert False
    
    def test_client_set_config_fields(self, client: Client):
        client.set_config({'org_id': 100})

        res = client.execute('SELECT * FROM bframe.customers')
        assert res.fetchone() == None
        assert client.config['env_id'] == 1

        client.set_config({'org_id': 1, 'contract_ids': ['88']})

        res = client.execute('SELECT * FROM bframe.contracts')
        assert len(res.fetchall()) == 1

    def test_client_config_property_cannot_be_set(self, client: Client):
        client.config['org_id'] =  100
        assert client.config['org_id'] == 1

    def test_client_set_config_cannot_set_unknown_properties(self, client: Client):
        try:
            client.set_config({'bacon': 'is good'})
        except:
            assert True
        else:
            assert False
    
    def test_client_set_config_set_rating_range_in_virtual(self, client: Client):
        client.set_config({'rating_range': ['2023-01-01', '2023-02-01']})
        
        try:
            client.set_config({'rating_range': []})
        except:
            assert True
        else:
            assert False

        try:
            client.set_config({'rating_range': None})
        except:
            assert True
        else:
            assert False

        try:
            client.set_config({'rating_range': 1})
        except:
            assert True
        else:
            assert False
    
    def test_client_set_config_set_forward_window_in_rolling(self, client: Client):
        client.set_config({
            'read_mode': 'CURRENT',
            'forward_window': 1,
        })
        
        try:
            client.set_config({
                'read_mode': 'CURRENT',
                'forward_window': None,
            })
        except:
            assert True
        else:
            assert False

        try:
            client.set_config({
                'read_mode': 'CURRENT',
                'forward_window': 'hello world',
            })
        except:
            assert True
        else:
            assert False
        
    def test_client_set_config_set_lookback_window_in_rolling(self, client: Client):
        client.set_config({
            'read_mode': 'CURRENT',
            'lookback_window': 1,
        })
        
        try:
            client.set_config({
                'read_mode': 'CURRENT',
                'lookback_window': None,
            })
        except:
            assert True
        else:
            assert False

        try:
            client.set_config({
                'read_mode': 'CURRENT',
                'lookback_window': 'hello world',
            })
        except:
            assert True
        else:
            assert False
        
    
    def test_client_init_remote_branch(self):
        branch_source_connect = "ATTACH ':memory:' AS brch;"
        client, _ = standard_duckdb_client(
            {'branch_id': 2},
            [
                DEFAULT_SOURCES[0],
                Source('branch', branch_source_connect, True)
            ],
        )

        # Check that queries work
        res = client.execute("SELECT * FROM bframe.contracts WHERE durable_id = '88'")
        contracts = res.df().to_dict('records')

        assert len(contracts) == 1

        # Check that adding things to the branch will be respected
        client.execute("INSERT INTO brch.customers (org_id, env_id, branch_id, id, durable_id, name, version) values (1, 1, 2, 2, '20', 'New version', 2);")
        customers = client.execute('SELECT * FROM bframe.customers WHERE id = 2').df().to_dict('records')

        assert customers[0]['name'] == 'New version'

    def test_client_existing_remote_branch(self, client: Client):
        client.set_config({
            'branch_id': 2,
        })

        branch_source_connect = "ATTACH ':memory:' AS brch;"
        client.set_source(Source('branch', branch_source_connect, True))

        # Check that queries work
        res = client.execute("SELECT * FROM bframe.contracts WHERE durable_id = '88'")
        contracts = res.df().to_dict('records')

        assert len(contracts) == 1

        # Check that adding things to the branch will be respected
        client.execute("INSERT INTO brch.customers (org_id, env_id, branch_id, id, durable_id, name, version) values (1, 1, 2, 2, '20', 'New version', 2);")
        customers = client.execute('SELECT * FROM bframe.customers WHERE id = 2').df().to_dict('records')

        assert customers[0]['name'] == 'New version'
    
    def test_remote_branch_views(self, client: Client):
        client.set_config({
            'branch_id': 2,
        })

        # The normal amount of invoices
        branch_source_connect = "ATTACH ':memory:' AS brch;"
        client.set_source(Source('branch', branch_source_connect, True))
        res = client.execute("SELECT * FROM bframe.invoices WHERE contract_id = '88';")
        invoices = res.df().to_dict('records')
        assert len(invoices) == 13

        # update the invoice schedule to happen every 2 months instead of 1
        client.execute("INSERT INTO brch.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule, version) values (1, 1, 2, 1, '10', 'test1', 'ARREARS', 2, 1);")

        res = client.execute("SELECT * FROM bframe.invoices WHERE contract_id = '88';")
        invoices = res.df().to_dict('records')
        assert len(invoices) == 7

    def test_client_init_events(self, client: Client):
        # org_id,env_id,branch_id,transaction_id,customer_id,properties,metered_at,received_at,customer_alias

        events_source_connect = """
            ATTACH ':memory:' AS evt;
            CREATE VIEW IF NOT EXISTS evt.events AS (
                SELECT *
                FROM read_csv('tests/fixtures/event_source.csv', header=true, columns={
                    'org_id': 'int64',
                    'env_id': 'int64',
                    'branch_id': 'int64',
                    'transaction_id': 'varchar',
                    'customer_id': 'varchar',
                    'properties': 'json',
                    'metered_at': 'timestamp',
                    'received_at': 'timestamp',
                    'customer_alias': 'varchar'
                })
            );
        """
        client.set_source(Source('events', events_source_connect, False))

        # Check that there is data in the new event store
        res = client.execute("SELECT * FROM bframe.events")
        events = res.df().to_dict('records')

        assert len(events) == 27

        # Check that views respect the new event store
        rated_events = client.execute("SELECT * FROM bframe.rated_events WHERE contract_id = '99'").df().to_dict('records')

        # The 27 events included along with the 23 empty rated events for other periods
        assert len(rated_events) == 50
