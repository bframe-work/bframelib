from bframelib import Client


class TestPricebooks:      
    def test_pricebook_deduplication(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.pricebooks WHERE durable_id = '80';")
        pricebooks = res.fetchdf().to_dict('records')
        assert len(pricebooks) == 1

        assert pricebooks[0]['invoice_schedule'] == 2