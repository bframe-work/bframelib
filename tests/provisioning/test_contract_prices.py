from bframelib import Client


class TestContractPrices:      
    def test_contract_price_deduplication(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.contract_prices WHERE id = 8;")
        contract_prices = res.fetchdf().to_dict('records')
        assert len(contract_prices) == 1

        assert contract_prices[0]['price'] == '0.02'