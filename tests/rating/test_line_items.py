
class TestLineItems:
    def test_insert_line_items(self, client):
        res = client.execute(f"INSERT INTO src.line_items BY NAME (SELECT '1' as id, * FROM bframe.line_items as li limit 1);")
        assert res.fetchone() == (1,)

    def test_generic_line_items(self, client):
        res = client.execute(f"SELECT * FROM bframe.line_items WHERE contract_id = '88' ORDER BY ended_at ASC;")
        line_items = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of line_items in the year, 12 for each month plus 1 upfront
        assert len(line_items) == 25
        
        # Pull all of the totals from each line item to ensure they reconcile
        totals = []
        for line_item in line_items:
            totals.append(line_item['amount'])
        assert sum(totals, 0) == 4*.25 + 1000 + 3*.5

    # Testing slowly changing dimensions (scd) on a month end change
    def test_scd_line_items(self, client):
        res = client.execute(f"SELECT * FROM bframe.line_items WHERE contract_id = '99' ORDER BY ended_at ASC;")
        line_items = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of line_items in the year, 12 for each month plus 1 upfront
        assert len(line_items) == 25
        
        # Pull all of the totals from each line item to ensure they reconcile
        totals = []
        for line_item in line_items:
            totals.append(line_item['amount'])
        assert sum(totals, 0) == 1*.25 + 2*.33 + 1000
    
    # Testing slowly changing dimensions (scd) on a mid-month change
    def test_mm_scd_line_items(self, client):
        res = client.execute(f"SELECT * FROM bframe.line_items WHERE contract_id = '100' ORDER BY ended_at ASC;")
        line_items = res.fetchdf().to_dict('records')

        # There are 4 line items normally + 1 fixed. In this test we do a contract change... this creates an additional 2 line items
        assert len(line_items) == 7
        
        # Pull all of the totals from each line item to ensure they reconcile
        totals = []
        for line_item in line_items:
            totals.append(line_item['amount'])
        # Only 2 out of 12 months should be counted, so the advanced charge is prorated
        assert sum(totals, 0) == round(1*.25, 2) + round(1*.33, 2) + round(1000 * (61/366), 2)
 
    # Test quarterly and offset contracts
    def test_offset_quarterly_contract_line_items(self, client):
        res = client.execute(f"SELECT * FROM bframe.line_items WHERE contract_id = '110' ORDER BY ended_at ASC;")
        line_items = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of line_items in the 12 month period (12/3 = 4 + 1 one time charge)
        assert len(line_items) == 5
        
        # Pull all of the totals from each line item to ensure they reconcile
        totals = []
        for line_item in line_items:
            totals.append(line_item['amount'])
        assert sum(totals, 0) == 4*.25 + 100

    # Test prices with a fixed_quantity
    def test_fixed_quantity_line_items(self, client):
        res = client.execute(f"SELECT * FROM bframe.line_items WHERE contract_id = '120' ORDER BY ended_at ASC;")
        line_items = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of line_items
        assert len(line_items) == 7
        
        # Pull all of the totals from each line item to ensure they reconcile
        totals = []
        for line_item in line_items:
            totals.append(line_item['amount'])
        expected = round(1*2*100*((59-1)/59), 2) + round(4*2*100, 2) + round(1*2*100*((61-55)/61), 2)  + round(1000*((365-56)/365), 2)
        assert sum(totals, 0) == expected
        
    # Test prices with a quantity contract override
    def test_fixed_quantity_line_items_with_override(self, client):
        res = client.execute(f"SELECT * FROM bframe.line_items WHERE contract_id = '140' ORDER BY ended_at ASC;")
        line_items = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of line_items
        assert len(line_items) == 13
        
        # Pull all of the totals from each line item to ensure they reconcile
        totals = []
        for line_item in line_items:
            totals.append(line_item['amount'])
        assert sum(totals, 0) == 12*.95*100 + 1000*3
    
    def test_line_items_solo_contract(self, client):
        res = client.execute(f"SELECT * FROM bframe.line_items WHERE contract_id = '190' ORDER BY ended_at ASC;")
        line_items = res.fetchdf().to_dict('records')
        assert len(line_items) == 4

        totals = []
        for line_item in line_items:
            totals.append(line_item['amount'])
        assert sum(totals, 0) == 4*55.34
    
    def test_line_items_override_contract_price_started_and_ended_at(self, client):
        res = client.execute(f"SELECT * FROM bframe.line_items WHERE contract_id = '200';")
        line_items = res.fetchdf().to_dict('records')
        assert len(line_items) == 1

        totals = []
        for line_item in line_items:
            totals.append(line_item['amount'])
        assert sum(totals, 0) == round(214/366*1000*-1, 2)

    # Test price schedules
    def test_price_schedule_line_items(self, client):
        res = client.execute(f"SELECT * FROM bframe.line_items WHERE contract_id = '150' ORDER BY ended_at ASC;")
        line_items = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of line_items
        assert len(line_items) == 12
        
        # Pull all of the totals from each line item to ensure they reconcile
        totals = []
        for line_item in line_items:
            totals.append(line_item['amount'])
        assert sum(totals, 0) == 2*100 + 10*999