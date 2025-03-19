import datetime
from bframelib import Client
from utils import apply_utc_on_cols


class TestContracts:  
    def test_single_contract(self, client: Client):
        client.set_config({'contract_ids': ['88']})
        res = client.execute(f"SELECT * FROM bframe.contracts;")
        
        contracts = res.fetchdf().to_dict('records')

        # Ensure only gets contracts associated with the durable key set
        assert len(contracts) == 1
        assert contracts[0]['durable_id'] == '88'

        # Ensure only invoices associated with the contract are received
        res = client.execute(f"SELECT * FROM bframe.invoices order by started_at;")
        invoices = res.fetchdf().to_dict('records')

        assert len(invoices) == 13

        for invoice in invoices:
            assert invoice['contract_id'] == '88'
    
    def test_contract_deduplication(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.contracts WHERE durable_id = '87';")
        df = res.df()
        apply_utc_on_cols(df)

        contracts = df.to_dict('records')
        assert len(contracts) == 1

        assert contracts[0]['ended_at'] == datetime.datetime(2024, 2, 1, tzinfo=datetime.timezone.utc)
    
    def test_void_contract(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.contracts WHERE durable_id = '220';")
        contracts = res.fetch_df().to_dict('records')

        # Ensure only gets contracts associated with the durable key set
        assert len(contracts) == 1
        assert contracts[0]['durable_id'] == '220'


        # Ensure no invoices associated with the contract are generated
        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '220';")
        invoices = res.fetchdf().to_dict('records')

        assert len(invoices) == 0

        # Ensure no price_spans associated with the contract are generated
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 17;")
        price_spans = res.fetchdf().to_dict('records')

        assert len(price_spans) == 0

        # Ensure no prices associated with the contract are generated
        res = client.execute(f"SELECT * FROM bframe.prices WHERE contract_uid = 17;")
        prices = res.fetchdf().to_dict('records')

        assert len(prices) == 0