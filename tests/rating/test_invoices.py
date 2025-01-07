
from bframelib import Client


class TestMainInvoices:
    def test_insert_invoices(self, client):
        res = client.execute(f"INSERT INTO src.invoices BY NAME (SELECT '1' as id, * FROM bframe.invoices limit 1);")
        assert res.fetchone() == (1,)
    
    def test_generic_invoices(self, client):
        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '88' ORDER BY ended_at ASC;")
        invoices = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of invoices in the year, 12 for each month plus 1 upfront
        assert len(invoices) == 13
        
        # Pull all of the totals from the invoice to ensure they reconcile
        totals = []
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == 4*.25 + 1000 + 3*.5

    # Testing slowly changing dimensions (scd) on a month end change
    def test_scd_invoices(self, client):
        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '99' ORDER BY ended_at ASC;")
        invoices = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of invoices in the year, 12 for each month plus 1 upfront
        assert len(invoices) == 13
        
        # Pull all of the totals from the invoice to ensure they reconcile
        totals = []
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == 1*.25 + 2*.33 + 1000

    # Testing slowly changing dimensions (scd) on a mid-month change
    def test_mm_scd_invoices(self, client):
        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '100' ORDER BY ended_at ASC;")
        invoices = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of invoices in the year, 12 for each month plus 1 upfront
        assert len(invoices) == 3
        
        # Pull all of the totals from the invoice to ensure they reconcile
        # Only 2 out of 12 months should be counted, so the advanced charge is prorated
        totals = []
        for invoice in invoices:
            totals.append(invoice['total'])
        expected = round(1*.25, 2) + round(1*.33, 2) + round(1000 * (61/366), 2)
        # Proration occurs in a leap year
        assert sum(totals, 0) == expected

    # Testing offset quarterly contracts
    def test_offset_quarterly_invoices(self, client):
        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '110' ORDER BY ended_at ASC;")
        invoices = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of invoices in the year, 12 for each month plus 1 upfront
        assert len(invoices) == 5
        
        # Pull all of the totals from the invoice to ensure they reconcile
        totals = []
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == 4*.25 + 100

class TestInvoicesLocal:
    def test_customer_local_branch(self, client: Client):
        client.set_config({'branch_id': 2})
        
        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '99';")
        invoices = res.fetchdf().to_dict('records')
        assert len(invoices) == 13

        totals = []
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == .66*2 + 1*.25 + 2*.33 + 1000