
import datetime
from bframelib.client import Client
from utils import apply_utc_on_cols


class TestRatedEvents:
    def test_insert_rated_events(self, client: Client):
        res = client.execute("INSERT INTO src.rated_events BY NAME (SELECT '1' as id, * FROM bframe.rated_events limit 1);")
        assert res.fetchone() == (1,)
    
    def test_empty_rated_event(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.rated_events WHERE contract_id = '88' AND ended_at = '2023-04-01';")
        df = res.df()
        apply_utc_on_cols(df)
        rated_events = df.to_dict('records')

        # There should be two rated events one for each product
        assert len(rated_events) == 2
        
        # Both rated events should be empty
        assert rated_events[0]['transaction_id'] == 'EMPTY_RATED_EVENT'
        assert rated_events[1]['transaction_id'] == 'EMPTY_RATED_EVENT'

        # Check the rated event has the necessary field values
        assert rated_events[0]['properties'] == '{}'
        assert rated_events[0]['metered_at'] == datetime.datetime(2023, 3, 1, tzinfo=datetime.timezone.utc)
        assert rated_events[0]['received_at'] == datetime.datetime(2023, 3, 1, tzinfo=datetime.timezone.utc)
        assert rated_events[0]['customer_id'] == '10'
    
    def test_generic_rated_events(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.rated_events WHERE contract_id = '88' ORDER BY metered_at ASC;")
        rated_events = res.fetchdf().to_dict('records')

        # There are 12 periods in a year and 2 line items with events in one period. There are 6 real events
        #  12 * 2 - 2 + 6 = 28 events
        assert len(rated_events) == 28
        
        # Pull each amount from rated events to ensure they reconcile
        totals = []
        for rated_event in rated_events:
            totals.append(rated_event['amount'])
        assert sum(totals, 0) == 4*.25 + 3*.5
    
    # Testing slowly changing dimensions (scd) on a month end change
    def test_scd_rated_events(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.rated_events WHERE contract_id = '99' ORDER BY metered_at ASC;")
        rated_events = res.fetchdf().to_dict('records')

        # There are 12 periods with real events across 2 of them. There are 2 relevant line items.
        # 12 * 2 - 2 + 3
        assert len(rated_events) == 25
        
        # Pull each amount from rated events to ensure they reconcile
        totals = []
        for rated_event in rated_events:
            totals.append(rated_event['amount'])
        assert sum(totals, 0) == 1*.25 + 2*.33

    # Testing slowly changing dimensions (scd) on a mid month change
    def test_scd_mm_rated_events(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.rated_events WHERE contract_id = '100' ORDER BY metered_at ASC;")
        rated_events = res.fetchdf().to_dict('records')

        # There are 2 periods but due to the contract change that increases to 3. There are 2 usage based products which doubles the line items.
        # There are 2 real events across 2 periods
        # 3 * 2 - 2 + 2 = 6
        assert len(rated_events) == 6
        
        # Pull each amount from rated events to ensure they reconcile
        totals = []
        for rated_event in rated_events:
            totals.append(rated_event['amount'])
        assert sum(totals, 0) == 1*.25 + 1*.33

    # Test quarterly and offset contracts
    def test_offset_quarterly_contract_rated_events(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.rated_events WHERE contract_id = '110' ORDER BY metered_at ASC;")
        rated_events = res.fetchdf().to_dict('records')

        # There were 4 real events across 3 periods. There are a total of 4 periods.
        # 4 - 3 + 4 = 5
        assert len(rated_events) == 5
        
        # Pull each amount from rated events to ensure they reconcile
        totals = []
        for rated_event in rated_events:
            totals.append(rated_event['amount'])
        assert sum(totals, 0) == 4*.25
    
    # Test customer SCDs
    def test_customer_scd_rated_events(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.rated_events WHERE contract_id = '160' ORDER BY metered_at ASC;")
        rated_events = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of rated_events (there are 8 actual rated events across 2 periods. 
        # There are 24 periods total. This means there would be 22 empty line items 22 + 8 = 30)
        assert len(rated_events) == 30
        
        # Pull each amount from rated events to ensure they reconcile
        totals = []
        for rated_event in rated_events:
            totals.append(rated_event['amount'])
        assert sum(totals, 0) == 8*.25