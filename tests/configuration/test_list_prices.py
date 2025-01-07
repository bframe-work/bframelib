from bframelib import Client


class TestListPrices:      
    def test_list_price_deduplication(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.list_prices WHERE id = 21;")
        list_prices = res.fetchdf().to_dict('records')
        assert len(list_prices) == 1

        assert list_prices[0]['price'] == '0.99'