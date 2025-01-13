from bframelib import Client
from utils import standard_duckdb_client

class TestBframeClient:
    def test_client_defaults(self):
        config = {
            'org_id': 1,
            'env_id': 1,
            'branch_id': 1
        }
        c = Client(config, init_core_schema=True)

        print(c.config)
        
        assert c.config['system_dt'] != None
        assert c.config['rating_as_of_dt'] != None
        assert c.config['contract_ids'] == []
        assert c.config['rating_range'] == []
        assert c.config['dedup_branch_events'] == False
        assert c.config['events_source'] == 'src.events'
    
    def test_client_init(self):
        config = {
            'org_id': 1,
            'env_id': 1,
            'branch_id': 1,
            'rating_range': ['1900-01-01', '2200-01-01'],
            'contract_ids': []
        }
        c = Client(config, init_core_schema=True)
        
        res = c.execute('SELECT * FROM bframe.customers')
        print(c.config)
        assert res.fetchone() == None
    
    def test_client_init_missing_required_fields(self):
        config = {
            'env_id': 1,
            'branch_id': 1,
        }
        
        try:
            Client(config, init_core_schema=True)
        except:
            assert True
        else:
            assert False

        config = {
            'org_id': 1,
            'branch_id': 1,
        }
        

        try:
            Client(config, init_core_schema=True)
        except:
            assert True
        else:
            assert False
        
        config = {
            'org_id': 1,
            'env_id': 1,
        }
        

        try:
            Client(config, init_core_schema=True)
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
    
    def test_client_init_remote_branch(self):
        client, _ = standard_duckdb_client(
            branch_id=2,
            branch_source_connect="ATTACH ':memory:' AS brch;"
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

        client.set_branch_source("ATTACH ':memory:' AS brch;", True)

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
        client.set_branch_source("ATTACH ':memory:' AS brch;", True)
        res = client.execute("SELECT * FROM bframe.invoices WHERE contract_id = '88';")
        invoices = res.df().to_dict('records')
        assert len(invoices) == 13

        # update the invoice schedule to happen every 2 months instead of 1
        client.execute("INSERT INTO brch.pricebooks (org_id, env_id, branch_id, id, durable_id, name, invoice_delivery, invoice_schedule, version) values (1, 1, 2, 1, '10', 'test1', 'ARREARS', 2, 1);")

        res = client.execute("SELECT * FROM bframe.invoices WHERE contract_id = '88';")
        invoices = res.df().to_dict('records')
        assert len(invoices) == 7


