
import json
from bframelib import Client

class TestLocalEvents:
    def test_branch_events_union(self, client: Client):
        client.set_config({"branch_id": 2})
        res = client.execute(f"SELECT * FROM bframe.events WHERE customer_id = 'random customer_id 1' ORDER BY received_at ASC;")
        events = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of matched_events for customer 1
        assert len(events) == 2
        assert events[0]['branch_id'] == 1
        assert events[1]['branch_id'] == 2

    def test_branch_events_union_with_duplicates(self, client: Client):
        client.set_config({"branch_id": 2, "dedup_branch_events": True})
        res = client.execute(f"SELECT * FROM bframe.events WHERE customer_id = 'random customer_id 2' ORDER BY received_at ASC;")
        events = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of matched_events for customer 2
        assert len(events) == 2
        assert events[0]['branch_id'] == 1
        assert events[1]['branch_id'] == 2

        properties = json.loads(events[1]['properties'])

        # Ensure that the event has been overriden (original event had 2 'cpu_hours')
        assert properties['cpu_hours'] == '5'