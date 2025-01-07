import datetime
    
class TestRatedDocumentsDateTimeTarget:
    def test_active_rated_docs(self, client):
        client.set_config({
            'rating_range': [],
            'rating_as_of_dt': datetime.datetime(2023, 12, 6, 23, 59, 59, 59, datetime.timezone.utc).isoformat(),
        })

        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '110';")
        invoices = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of invoices there should only be a one time invoice and an arrears invoice
        assert len(invoices) == 2
        
        # Pull all of the totals from the invoice to ensure they reconcile
        totals = []
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == 1*.25 + 100
    
    def test_inactive_rated_docs(self, client):
        client.set_config({
            'rating_range': [],
            'rating_as_of_dt': datetime.datetime(2023, 12, 7, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
        })

        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '110';")
        invoices = res.fetchdf().to_dict('records')

        # Ensure there are no invoices since this is exactly one second after the inclusion period
        assert len(invoices) == 0

    def test_range_of_rated_docs(self, client):
        client.set_config({
            'rating_range': [
                datetime.datetime(2023, 1, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
                datetime.datetime(2023, 7, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat()
            ],
        })

        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '110' ORDER BY ended_at ASC;")
        invoices = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of invoices there should only be a one time invoice and and 2 arrears invoice
        assert len(invoices) == 3
        
        # Pull all of the totals from the invoice to ensure they reconcile
        totals = []
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == 100 + 3*.25
