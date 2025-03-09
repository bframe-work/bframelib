import datetime
from bframelib import Client
    
class TestRatedDocumentsDateTimeTarget:
    
    def test_virtual_read_mode(self, client: Client):
        client.set_config({
            'rating_range': [
                datetime.datetime(2023, 1, 2, 0, 0, 1, 0, datetime.timezone.utc).isoformat(),
                datetime.datetime(2023, 1, 31, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
            ],
        })

        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '110';")
        invoices = res.fetchdf().to_dict('records')
        print(invoices)

        # Ensure there are no invoices since this is exactly one second after the inclusion period
        assert len(invoices) == 0

        client.set_config({
            'rating_range': [
                datetime.datetime(2023, 1, 2, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
                datetime.datetime(2023, 1, 31, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
            ],
        })

        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '110';")
        invoices = res.fetchdf().to_dict('records')

        # There should be an invoice since this is exactly in the inclusion period
        assert len(invoices) == 1

        # Pull all of the totals from the invoice to ensure they reconcile
        totals = []
        
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == 0
    
    def test_stored_read_mode(self, client: Client):
        client.set_config({
            'rating_range': [
                datetime.datetime(2023, 1, 2, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
                datetime.datetime(2023, 3, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
            ],
        })

        client.execute("""
            CREATE TEMP TABLE t1 AS (SELECT * FROM bframe.invoices WHERE contract_id = '110');
            CREATE TEMP TABLE t2 AS (SELECT * FROM bframe.line_items WHERE contract_id = '110');
            
            INSERT INTO src.invoices BY NAME (SELECT * FROM t1);
            INSERT INTO src.line_items BY NAME (SELECT * FROM t2);
        """)

        client.set_config({
            'read_mode': 'STORED',
            'stored_rating_range': [
                datetime.datetime(2023, 1, 2, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
                datetime.datetime(2023, 3, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
            ],
        })

        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '110';")
        invoices = res.fetchdf().to_dict('records')
        print(invoices)

        # Ensure there are the correct number of invoices
        assert len(invoices) == 2
        
        # Pull all of the totals from the invoice to ensure they reconcile
        totals = []
        
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == 1*.25 + 100

    def test_hybrid_read_mode(self, client: Client):
        client.set_config({
            'rating_range': [
                datetime.datetime(2023, 1, 2, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
                datetime.datetime(2023, 6, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
            ],
        })

        client.execute("""
            CREATE TEMP TABLE t1 AS (SELECT * FROM bframe.invoices WHERE contract_id = '110');
            CREATE TEMP TABLE t2 AS (SELECT * FROM bframe.line_items WHERE contract_id = '110');
            
            INSERT INTO src.invoices BY NAME (SELECT * FROM t1);
            INSERT INTO src.line_items BY NAME (SELECT * FROM t2);
        """)

        client.set_config({
            'read_mode': 'HYBRID',
            'stored_rating_range': [
                datetime.datetime(2023, 1, 2, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
                datetime.datetime(2023, 6, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
            ],
            'rating_range': [
                datetime.datetime(2023, 6, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
                datetime.datetime(2024, 1, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
            ],
        })

        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '110';")
        invoices = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of invoices
        assert len(invoices) == 5
        
        # Pull all of the totals from the invoice to ensure they reconcile
        totals = []
        
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == 4*.25 + 100

        # Check that only stored invoices are returned (basicall checks if hybrid actually works)
        client.set_config({'read_mode': 'STORED'})

        res = client.execute(f"SELECT * FROM bframe.invoices WHERE contract_id = '110';")
        invoices = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of invoices
        assert len(invoices) == 3
        
        # Pull all of the totals from the invoice to ensure they reconcile
        totals = []
        
        for invoice in invoices:
            totals.append(invoice['total'])
        assert sum(totals, 0) == 3*.25 + 100

    
    def test_virtual_unstored_read_mode(self, client: Client):
        invoices = client.execute("SELECT * FROM bframe.invoices ORDER BY id").fetchall()
        line_items = client.execute("SELECT * FROM bframe.line_items ORDER BY id").fetchall()

        # SQLite does not handle the circular read and insertion well, we end up with a unique constraint
        # error if we insert bframe.invoices directly. This problem some how goes away if
        # the table is ordered (which I don't fully understand why). I think it's easier to understand
        # the solution by using a temp table which also works.
        client.set_config({'read_mode': 'UNSTORED_VIRTUAL'})
        client.execute("""
            CREATE TEMP TABLE t1 AS (SELECT * FROM bframe.invoices);
            CREATE TEMP TABLE t2 AS (SELECT * FROM bframe.line_items);
            
            INSERT INTO src.invoices BY NAME (SELECT * FROM t1);
            INSERT INTO src.line_items BY NAME (SELECT * FROM t2);
        """)

        client.set_config({'read_mode': 'STORED'})
        new_invoices = client.execute("SELECT * FROM bframe.invoices ORDER BY id").fetchall()
        new_line_items = client.execute("SELECT * FROM bframe.line_items ORDER BY id").fetchall()

        # Persisting invoices should result in the same data if it's pulled from the same date range
        assert len(invoices) == len(new_invoices)
        for i in range(len(invoices)):
            assert invoices[i] == new_invoices[i]

        assert len(line_items) == len(new_line_items)
        for i in range(len(line_items)):
            assert line_items[i] == new_line_items[i]


        # If we look at net window again it should be empty
        client.set_config({'read_mode': 'UNSTORED_VIRTUAL'})
        repeat_invoice_count = len(client.execute("SELECT * FROM bframe.invoices").fetchall())
        repeat_line_item_count = len(client.execute("SELECT * FROM bframe.line_items").fetchall())

        assert repeat_invoice_count == 0
        assert repeat_line_item_count == 0
    
    def test_changes_to_pricing(self, client: Client):
        client.set_config({
            'rating_as_of_dt': datetime.datetime(2023, 11, 15, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
            'rating_range': [
                datetime.datetime(2023, 1, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
                datetime.datetime(2023, 11, 1, 0, 0, 0, 0, datetime.timezone.utc).isoformat(),
            ],
        })
        
        # Persist all invoices
        client.execute("""
            CREATE TEMP TABLE t1 AS (SELECT * FROM bframe.invoices WHERE status = 'FINALIZED');
            CREATE TEMP TABLE t2 AS (SELECT * FROM bframe.line_items WHERE status = 'FINALIZED');
                       
            INSERT INTO src.invoices BY NAME (SELECT * FROM t1);
            INSERT INTO src.line_items BY NAME (SELECT * FROM t2);
        """)

        # Set to stored and update pricing
        client.set_config({
            'read_mode': 'STORED',
        })
        invoices = client.execute("SELECT * FROM bframe.invoices WHERE status = 'FINALIZED' ORDER BY id").fetchall()
        line_items = client.execute("SELECT * FROM bframe.line_items WHERE status = 'FINALIZED' ORDER BY id").fetchall()

        client.execute("""
            INSERT INTO src.contract_prices (org_id, env_id, branch_id, id, list_price_uid, contract_uid, invoice_schedule, fixed_quantity, version) values (1, 1, 1, 3, 10, 9, 1, '5.00', 2);
        """)

        new_invoices = client.execute("SELECT * FROM bframe.invoices WHERE status = 'FINALIZED' ORDER BY id").fetchall()
        new_line_items = client.execute("SELECT * FROM bframe.line_items WHERE status = 'FINALIZED' ORDER BY id").fetchall()

        for i in range(len(invoices)):
            assert invoices[i] == new_invoices[i]
        
        for i in range(len(line_items)):
            assert line_items[i] == new_line_items[i]


    def test_range_of_rated_docs(self, client: Client):
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
