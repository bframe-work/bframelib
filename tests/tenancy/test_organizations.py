from bframelib import Client


class TestOrganizations:      
    
    def test_organization_correct(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.organizations WHERE id = 1;")
        orgs = res.fetchdf().to_dict('records')
        assert len(orgs) == 1
        assert orgs[0]['name'] == 'Big Co'

    