
class TestProcessedEvents:
    def test_insert_processed_event(self, client):
        res = client.execute(f"INSERT INTO src.processed_events BY NAME (SELECT * FROM bframe.processed_events limit 1);")
        assert res.fetchone() == (1,)

    def test_customer_ingest_alias(self, client):
        # Test that the ingest alias resolves to the correct customer_id
        res = client.execute(f"SELECT * FROM bframe.processed_events WHERE customer_alias = 'holy_bread' and resolved_customer_id = '10';")
        processedEvents = res.fetchdf().to_dict('records')
        assert len(processedEvents) == 1

        # Test that the second ingest alias resolves to the correct customer_id
        res = client.execute(f"SELECT * FROM bframe.processed_events WHERE customer_alias = 'carb_wheels' and resolved_customer_id = '10';")
        processedEvents = res.fetchdf().to_dict('records')
        assert len(processedEvents) == 1

    def test_customer_scd_customer_resolution(self, client):
        res = client.execute(f"SELECT * FROM bframe.processed_events WHERE resolved_customer_id = '90';")
        processedEvents = res.fetchdf().to_dict('records')
        assert len(processedEvents) == 8

