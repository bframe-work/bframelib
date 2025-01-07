from bframelib import Client


class TestEnvironments:      
    def test_environments_filtering(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.environments WHERE org_id = 2;")
        environments = res.fetchdf().to_dict('records')
        assert len(environments) == 0
    
    def test_env_correct(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.environments WHERE name = 'PROD';")
        branches = res.fetchdf().to_dict('records')
        assert len(branches) == 1
        assert branches[0]['id'] == 1

    