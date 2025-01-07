from bframelib import Client


class TestBranches:      
    def test_branch_filtering(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.branches WHERE org_id = 2;")
        branches = res.fetchdf().to_dict('records')
        assert len(branches) == 0
    
    def test_branch_correct(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.branches WHERE id = 1;")
        branches = res.fetchdf().to_dict('records')
        assert len(branches) == 1
        assert branches[0]['name'] == 'main'

    