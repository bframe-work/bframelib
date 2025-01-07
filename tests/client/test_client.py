from bframelib import Client

class TestBframeClient:
    def test_client_defaults(self):
        args = {
            'org_id': 1,
            'env_id': 1,
            'branch_id': 1
        }
        c = Client(init_client=True, **args)

        print(c.config)
        
        assert c.config['system_dt'] != None
        assert c.config['rating_as_of_dt'] != None
        assert c.config['contract_ids'] == []
        assert c.config['rating_range'] == []
        assert c.config['dedup_branch_events'] == False
        assert c.config['events_source'] == 'src.events'
    
    def test_client_init(self):
        args = {
            'org_id': 1,
            'env_id': 1,
            'branch_id': 1,
            'rating_range': ['1900-01-01', '2200-01-01'],
            'contract_ids': []
        }
        c = Client(init_client=True, **args)
        
        res = c.execute('SELECT * FROM bframe.customers')
        print(c.config)
        assert res.fetchone() == None
    
    def test_client_init_missing_required_fields(self):
        args = {
            'env_id': 1,
            'branch_id': 1,
        }
        
        try:
            Client(init_client=True, **args)
        except:
            assert True
        else:
            assert False

        args = {
            'org_id': 1,
            'branch_id': 1,
        }
        

        try:
            Client(init_client=True, **args)
        except:
            assert True
        else:
            assert False
        
        args = {
            'org_id': 1,
            'env_id': 1,
        }
        

        try:
            Client(init_client=True, **args)
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

