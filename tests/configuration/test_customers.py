from bframelib import Client

class TestCustomersMain:
    def test_customer_main_branch(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.customers WHERE id = 2")
        customer = res.fetchdf().to_dict('records')[0]
        assert customer['name'] == 'Crack city'

        # Local results aren't included in the main branch
        res = client.execute(f"SELECT * FROM bframe.customers WHERE id = 2 and version = 2")
        customer = res.fetchdf().to_dict('records')
        assert len(customer) == 0

class TestCustomersLocalBranch:
    def test_customer_local_branch(self, client: Client):
        client.set_config({'branch_id': 2})
        res = client.execute(f"SELECT * FROM bframe.customers WHERE id = 2")
        customer = res.fetchdf().to_dict('records')[0]
        assert customer['name'] == 'Stack City'
