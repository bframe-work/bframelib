from bframelib import Client


class TestProducts:      
    def test_product_deduplication(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.products WHERE id = 5;")
        products = res.fetchdf().to_dict('records')
        assert len(products) == 1

        assert products[0]['ptype'] == 'FAKE'