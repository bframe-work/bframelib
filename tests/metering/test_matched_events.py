
import datetime
import json
from bframelib.client import Client
from utils import apply_utc_on_cols


class TestMatchedEvents:
    def test_insert_matched_event(self, client):
        res = client.execute(f"INSERT INTO src.matched_events BY NAME (SELECT * FROM bframe.matched_events limit 1);")
        assert res.fetchone() == (1,)

    def test_count_matched_events(self, client):
        res = client.execute(f"SELECT * FROM bframe.matched_events WHERE product_uid = 1 and customer_id = '10' ORDER BY metered_at ASC;")
        matched_events = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of matched_events for customer 1
        assert len(matched_events) == 4
        quantity = 0
        for event in matched_events:
            quantity = quantity + event['quantity']

        # Check if the quantity is correct
        assert quantity == 4

    def test_sum_matched_events(self, client):
        res = client.execute(f"SELECT * FROM bframe.matched_events WHERE product_uid = 3 and customer_id = '10' ORDER BY metered_at ASC;")
        matched_events = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of matched_events. This includes all events not just those for one customer
        assert len(matched_events) == 2
        quantity = 0
        for event in matched_events:
            quantity = quantity + event['quantity']

        # Check if the quantity is correct
        assert quantity == 3
    
    def test_multi_filters(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.matched_events WHERE product_uid = 6 and customer_id = '150' ORDER BY metered_at ASC;")
        df = res.df()
        apply_utc_on_cols(df)
        matched_events = df.to_dict('records')

        # Ensure there are the correct number of matched_events. This includes all events not just those for one customer
        assert len(matched_events) == 2

        # Check if the quantity is correct
        assert matched_events[0]['metered_at'] == datetime.datetime(2023, 12, 2, 1, tzinfo=datetime.timezone.utc)
        assert json.loads(matched_events[0]['properties']).get('region', None) == None
        assert json.loads(matched_events[1]['properties'])['region'] == 'us-east-1'