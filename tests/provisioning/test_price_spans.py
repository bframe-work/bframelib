import calendar
import datetime
import numpy

from bframelib import Client

YEAR = 2023

class TestPriceSpans:
    def test_insert_price_span(self, client: Client):
        res = client.execute(f"INSERT INTO src.price_spans BY NAME (SELECT * FROM bframe.price_spans limit 1);")
        assert res.fetchone() == (1,)

    def test_usage_price_spans(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE product_uid = 1 and contract_uid = 1 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of price spans for the product in the year
        assert len(price_spans) == 12
        dates = []
        for month in range(1, 13):
            last_day = calendar.monthrange(YEAR, month)[1]
            start_of_month_dt = datetime.datetime(year=YEAR, month=month, day=1)
            next_month_dt = datetime.datetime(year=YEAR, month=month, day=last_day) + datetime.timedelta(days=1)
            dates.append((start_of_month_dt, next_month_dt))

        # Check each price span
        for i, price_span in enumerate(price_spans):
            started_at = dates[i][0]
            ended_at = dates[i][1]
            assert price_span['started_at'] == started_at
            assert price_span['ended_at'] == ended_at
            assert price_span['price'] == '0.25'
            assert price_span['product_type'] == 'EVENT'
            assert price_span['product_uid'] == 1
            assert price_span['pricebook_id'] == '10'
            assert price_span['contract_uid'] == 1
            assert price_span['customer_id'] == '10'
    
    def test_fixed_price_spans(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE product_uid = 2 and contract_uid = 1 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of price spans in the year
        assert len(price_spans) == 1
        price_span = price_spans[0]

        # Advanced pricing is an instant invoice at the beginning of the month
        started_at = datetime.datetime(2023, 1, 1)
        ended_at = datetime.datetime(2024, 1, 1)

        # Check each price span field
        assert price_span['started_at'] == started_at
        assert price_span['ended_at'] == ended_at
        assert price_span['effective_at'] == started_at
        assert price_span['ineffective_at'] == ended_at
        assert price_span['price'] == '1000'
        assert price_span['product_type'] == 'FIXED'
        assert price_span['product_uid'] == 2
        assert price_span['pricebook_id'] == '10'
        assert price_span['contract_uid'] == 1
        assert price_span['customer_id'] == '10'

    # Testing slowly changing dimensions (scd) on a month end change
    def test_all_price_spans_scd(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_id = '99' ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of price spans in the year
        assert len(price_spans) == 25
    
    # Look at the actual price spans that are generated from the SCD
    def test_price_spans_on_contract_change_scd(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 3 and product_uid = 3 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of price spans in the 6 month period of the specific contract effective period
        assert len(price_spans) == 6

        # This contract is only for the back 6 months of the year
        dates = []
        for month in range(7, 13):
            last_day = calendar.monthrange(YEAR, month)[1]
            start_of_month_dt = datetime.datetime(year=YEAR, month=month, day=1)
            next_month_dt = datetime.datetime(year=YEAR, month=month, day=last_day) + datetime.timedelta(days=1)
            dates.append((start_of_month_dt, next_month_dt))

        # Check each price span
        for i, price_span in enumerate(price_spans):
            started_at = dates[i][0]
            ended_at = dates[i][1]
            assert price_span['started_at'] == started_at
            assert price_span['ended_at'] == ended_at
            assert price_span['effective_at'] == started_at
            assert price_span['ineffective_at'] == ended_at
            assert price_span['price'] == '0.66'
            assert price_span['product_type'] == 'EVENT'
            assert price_span['product_uid'] == 3
            assert price_span['pricebook_id'] == '20'
            assert price_span['contract_uid'] == 3
            assert price_span['customer_id'] == '20'
    
    # Testing slowly changing dimensions (scd) on a mid-month change
    def test_all_price_spans_mm_scd(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_id = '100' ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')

        # Ensure there are the correct number of price spans in the 2 month period
        assert len(price_spans) == 7
    
    # Look at the actual price spans that are generated from the MM SCD
    def test_event_price_spans_on_mm_contract_change_scd(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 5 and product_uid = 1 ORDER BY ended_at ASC;")
        price_span = res.fetchdf().to_dict('records')[0]

        # Check price span
        assert price_span['started_at'] == datetime.datetime(2023, 12, 1)
        assert price_span['ended_at'] == datetime.datetime(2024, 1, 1)
        assert price_span['effective_at'] == datetime.datetime(2023, 12, 11)
        assert price_span['ineffective_at'] == datetime.datetime(2024, 1, 1)
        assert price_span['price'] == '0.33'
        assert price_span['product_type'] == 'EVENT'
        assert price_span['product_uid'] == 1
        assert price_span['pricebook_id'] == '20'
        assert price_span['contract_id'] == '100'
        assert price_span['contract_uid'] == 5
        assert price_span['customer_id'] == '30'
    
    def test_fixed_price_spans_on_mm_contract_change_scd(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_id = '100' and product_uid = 2 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 1

        price_span = price_spans[0]

        # Check price span
        # This tests that the contract end caps the advanced charge end which can be seen in the proration dates
        assert price_span['started_at'] == datetime.datetime(2023, 11, 1)
        assert price_span['ended_at'] == datetime.datetime(2024, 1, 1)
        assert price_span['effective_at'] == datetime.datetime(2023, 11, 1)
        assert price_span['ineffective_at'] == datetime.datetime(2024, 1, 1)
        assert price_span['proration_start'] == datetime.datetime(2023, 11, 1)
        assert price_span['proration_end'] == datetime.datetime(2024, 11, 1)
        assert price_span['price'] == '1000'
        assert price_span['product_type'] == 'FIXED'
        assert price_span['product_uid'] == 2
        assert price_span['pricebook_id'] == '10'
        assert price_span['contract_id'] == '100'
        assert price_span['contract_uid'] == 4
        assert price_span['customer_id'] == '30'

    def test_price_spans_on_offset_dates_and_quarterly_invoice_schedule(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 6 and product_uid = 1 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 4

        start_price_span = price_spans[0]
        end_price_span = price_spans[3]
        
        assert start_price_span['started_at'] == datetime.datetime(2023, 1, 2)
        assert start_price_span['ended_at'] == datetime.datetime(2023, 4, 1)
        assert start_price_span['effective_at'] == datetime.datetime(2023, 1, 2)
        assert start_price_span['ineffective_at'] == datetime.datetime(2023, 4, 1)
        assert start_price_span['price'] == '0.25'
        assert start_price_span['product_type'] == 'EVENT'
        assert start_price_span['product_uid'] == 1
        assert start_price_span['pricebook_id'] == '30'
        assert start_price_span['contract_id'] == '110'
        assert start_price_span['contract_uid'] == 6
        assert start_price_span['customer_id'] == '40'

        assert end_price_span['started_at'] == datetime.datetime(2023, 10, 1)
        assert end_price_span['ended_at'] == datetime.datetime(2023, 12, 7)
        assert end_price_span['effective_at'] == datetime.datetime(2023, 10, 1)
        assert end_price_span['ineffective_at'] == datetime.datetime(2023, 12, 7)
        assert end_price_span['price'] == '0.25'
        assert end_price_span['product_type'] == 'EVENT'
        assert end_price_span['product_uid'] == 1
        assert end_price_span['pricebook_id'] == '30'
        assert end_price_span['contract_id'] == '110'
        assert end_price_span['contract_uid'] == 6
        assert end_price_span['customer_id'] == '40'
    
    def test_price_spans_on_offset_one_time_charge(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 6 and product_uid = 2 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 1

        price_span = price_spans[0]
        
        assert price_span['started_at'] == datetime.datetime(2023, 2, 1)
        assert price_span['ended_at'] == datetime.datetime(2023, 12, 7)
        assert price_span['effective_at'] == datetime.datetime(2023, 2, 1)
        assert price_span['ineffective_at'] == datetime.datetime(2023, 12, 7)
        assert price_span['price'] == '100'
        assert price_span['product_type'] == 'FIXED'
        assert price_span['product_uid'] == 2
        assert price_span['pricebook_id'] == '30'
        assert price_span['contract_id'] == '110'
        assert price_span['contract_uid'] == 6
        assert price_span['customer_id'] == '40'
    
    def test_proration_range_for_advanced_price_spans(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 7 AND product_uid = 2 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 1

        price_span = price_spans[0]

        # The proration range should cover the entire months that are supposed to be allocated based on the invoice schedule
        # This allows us the proration to work as intended
        assert price_span['proration_start'] == datetime.datetime(2023, 1, 1)
        assert price_span['proration_end'] == datetime.datetime(2024, 1, 1)

        # This is just checking everyting else functions as normal
        assert price_span['started_at'] == datetime.datetime(2023, 1, 2)
        assert price_span['ended_at'] == datetime.datetime(2023, 11, 7)
        assert price_span['effective_at'] == datetime.datetime(2023, 1, 2)
        assert price_span['ineffective_at'] == datetime.datetime(2023, 11, 7)
        assert price_span['price'] == '1000'
        assert price_span['product_type'] == 'FIXED'
        assert price_span['product_uid'] == 2
        assert price_span['pricebook_id'] == '40'
        assert price_span['contract_id'] == '120'
        assert price_span['contract_uid'] == 7
        assert price_span['customer_id'] == '50'

    def test_proration_range_for_arrears_price_spans(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 7 AND product_uid = 4 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 6

        first_price_span = price_spans[0]
        last_price_span = price_spans[-1]

        # The proration range should cover the entire months that are supposed to be allocated based on the invoice schedule
        # This allows us the proration to work as intended
        assert first_price_span['proration_start'] == datetime.datetime(2023, 1, 1)
        assert first_price_span['proration_end'] == datetime.datetime(2023, 3, 1)
        assert first_price_span['started_at'] == datetime.datetime(2023, 1, 2)
        assert first_price_span['ended_at'] == datetime.datetime(2023, 3, 1)
        assert first_price_span['effective_at'] == datetime.datetime(2023, 1, 2)
        assert first_price_span['ineffective_at'] == datetime.datetime(2023, 3, 1)

        # Test on the other end of the spectrum
        assert last_price_span['proration_start'] == datetime.datetime(2023, 11, 1)
        assert last_price_span['proration_end'] == datetime.datetime(2024, 1, 1)
        assert last_price_span['started_at'] == datetime.datetime(2023, 11, 1)
        assert last_price_span['ended_at'] == datetime.datetime(2023, 11, 7)
        assert last_price_span['effective_at'] == datetime.datetime(2023, 11, 1)
        assert last_price_span['ineffective_at'] == datetime.datetime(2023, 11, 7)
    
    def test_fixed_contract_price_spans(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 8 AND product_uid = 2 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 3

        dates = (
            (datetime.datetime(2023, 1, 1), datetime.datetime(2023, 5, 1)),
            (datetime.datetime(2023, 5, 1), datetime.datetime(2023, 9, 1)),
            (datetime.datetime(2023, 9, 1), datetime.datetime(2024, 1, 1))
        )

        for i, price_span in enumerate(price_spans):
            started_at = dates[i][0]
            ended_at = dates[i][1]
            assert price_span['started_at'] == started_at
            assert price_span['ended_at'] == ended_at
            assert price_span['price'] == '12345'
            assert price_span['product_type'] == 'FIXED'
            assert price_span['product_uid'] == 2
            assert price_span['pricebook_id'] == '10'
            assert price_span['contract_id'] == '130'
            assert price_span['customer_id'] == '60'
    
    def test_contract_solo_contract_price_spans(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 14 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 4

        dates = (
            (datetime.datetime(2023, 1, 1), datetime.datetime(2023, 4, 1)),
            (datetime.datetime(2023, 4, 1), datetime.datetime(2023, 7, 1)),
            (datetime.datetime(2023, 7, 1), datetime.datetime(2023, 10, 1)),
            (datetime.datetime(2023, 10, 1), datetime.datetime(2024, 1, 1))
        )

        for i, price_span in enumerate(price_spans):
            started_at = dates[i][0]
            ended_at = dates[i][1]
            assert price_span['started_at'] == started_at
            assert price_span['ended_at'] == ended_at
            assert price_span['price'] == '55.34'
            assert price_span['product_type'] == 'FIXED'
            assert price_span['invoice_delivery'] == 'ADVANCED'
            assert price_span['product_uid'] == 4
            assert price_span['pricebook_id'] == None
            assert numpy.isnan(price_span['list_price_uid'])
            assert price_span['contract_id'] == '190'
            assert price_span['customer_id'] == '120'
    
    def test_price_schedule_part_one(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 10 AND list_price_uid = 11 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 2

        dates = (
            (datetime.datetime(2023, 1, 1), datetime.datetime(2023, 2, 1)),
            (datetime.datetime(2023, 2, 1), datetime.datetime(2023, 3, 1))
        )

        for i, price_span in enumerate(price_spans):
            started_at = dates[i][0]
            ended_at = dates[i][1]
            assert price_span['started_at'] == started_at
            assert price_span['ended_at'] == ended_at
            assert price_span['price'] == '100'
            assert price_span['product_type'] == 'FIXED'
            assert price_span['product_uid'] == 2
            assert price_span['pricebook_id'] == '50'
            assert price_span['contract_id'] == '150'
            assert price_span['customer_id'] == '80'

    def test_price_schedule_part_two(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 10 AND list_price_uid = 12 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 10

        dates = (
            (datetime.datetime(2023, 3, 1), datetime.datetime(2023, 4, 1)),
            (datetime.datetime(2023, 4, 1), datetime.datetime(2023, 5, 1)),
            (datetime.datetime(2023, 5, 1), datetime.datetime(2023, 6, 1)),
            (datetime.datetime(2023, 6, 1), datetime.datetime(2023, 7, 1)),
            (datetime.datetime(2023, 7, 1), datetime.datetime(2023, 8, 1)),
            (datetime.datetime(2023, 8, 1), datetime.datetime(2023, 9, 1)),
            (datetime.datetime(2023, 9, 1), datetime.datetime(2023, 10, 1)),
            (datetime.datetime(2023, 10, 1), datetime.datetime(2023, 11, 1)),
            (datetime.datetime(2023, 11, 1), datetime.datetime(2023, 12, 1)),
            (datetime.datetime(2023, 12, 1), datetime.datetime(2024, 1, 1))
        )

        for i, price_span in enumerate(price_spans):
            started_at = dates[i][0]
            ended_at = dates[i][1]
            assert price_span['started_at'] == started_at
            assert price_span['ended_at'] == ended_at
            assert price_span['price'] == '999'
            assert price_span['product_type'] == 'FIXED'
            assert price_span['product_uid'] == 2
            assert price_span['pricebook_id'] == '50'
            assert price_span['contract_id'] == '150'
            assert price_span['customer_id'] == '80'
    
    def test_contract_with_contract_price_started_and_ended_at(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 15;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 1
        price_span = price_spans[0]

        assert price_span['started_at'] == datetime.datetime(2023, 6, 1)
        assert price_span['ended_at'] == datetime.datetime(2024, 1, 1)
        assert price_span['proration_start'] == datetime.datetime(2023, 6, 1)
        assert price_span['proration_end'] == datetime.datetime(2024, 6, 1)
        assert price_span['price'] == '-1000.00'
        assert price_span['product_type'] == 'FIXED'
        assert price_span['product_uid'] == 4
        assert price_span['contract_id'] == '200'
        assert price_span['customer_id'] == '120'
    
    def test_pricebook_slowly_changing_dimensions_event_product(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_id = '170' AND product_uid = 1 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 6

        expected_price_spans = (
            (datetime.datetime(2023, 1, 1), datetime.datetime(2023, 2, 1), '0.33'),
            (datetime.datetime(2023, 2, 1), datetime.datetime(2023, 3, 1), '0.33'),
            (datetime.datetime(2023, 3, 1), datetime.datetime(2023, 4, 1), '0.33'),
            (datetime.datetime(2023, 4, 1), datetime.datetime(2023, 5, 1), '0.33'),
            (datetime.datetime(2023, 7, 1), datetime.datetime(2023, 10, 1), '0.22'),
            (datetime.datetime(2023, 10, 1), datetime.datetime(2024, 1, 1), '0.22'),
        )

        for i, price_span in enumerate(price_spans):
            started_at = expected_price_spans[i][0]
            ended_at = expected_price_spans[i][1]
            price = expected_price_spans[i][2]
            assert price_span['started_at'] == started_at
            assert price_span['ended_at'] == ended_at
            assert price_span['price'] == price
            assert price_span['product_type'] == 'EVENT'
            assert price_span['product_uid'] == 1
            assert price_span['pricebook_id'] == '60'
            assert price_span['contract_id'] == '170'
            assert price_span['customer_id'] == '100'
    
    def test_pricebook_slowly_changing_dimensions_fixed_product(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_id = '170' AND product_uid = 2 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 1
        price_span = price_spans[0]

        assert price_span['started_at'] == datetime.datetime(2023, 1, 1)
        assert price_span['ended_at'] == datetime.datetime(2024, 1, 1)
        assert price_span['price'] == '1000'
        assert price_span['product_type'] == 'FIXED'
        assert price_span['product_uid'] == 2
        assert price_span['pricebook_id'] == '60'
        assert price_span['contract_id'] == '170'
        assert price_span['customer_id'] == '100'

    def test_long_dated_contract_with_offset_start_date_and_7_month_invoice_schedule(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_id = '180' AND product_uid = 2 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        assert len(price_spans) == 12

        dates = (
            (datetime.datetime(2021, 7, 10), datetime.datetime(2022, 2, 1)),
            (datetime.datetime(2022, 2, 1), datetime.datetime(2022, 9, 1)),
            (datetime.datetime(2022, 9, 1), datetime.datetime(2023, 4, 1)),
            (datetime.datetime(2023, 4, 1), datetime.datetime(2023, 11, 1)),
            (datetime.datetime(2023, 11, 1), datetime.datetime(2024, 6, 1)),
            (datetime.datetime(2024, 6, 1), datetime.datetime(2025, 1, 1)),
            (datetime.datetime(2025, 1, 1), datetime.datetime(2025, 8, 1)),
            (datetime.datetime(2025, 8, 1), datetime.datetime(2026, 3, 1)),
            (datetime.datetime(2026, 3, 1), datetime.datetime(2026, 10, 1)),
            (datetime.datetime(2026, 10, 1), datetime.datetime(2027, 5, 1)),
            (datetime.datetime(2027, 5, 1), datetime.datetime(2027, 12, 1)),
            (datetime.datetime(2027, 12, 1), datetime.datetime(2028, 1, 1)),
        )

        for i, price_span in enumerate(price_spans):
            started_at = dates[i][0]
            ended_at = dates[i][1]
            assert price_span['started_at'] == started_at
            assert price_span['ended_at'] == ended_at
            assert price_span['price'] == '1000'
            assert price_span['product_type'] == 'FIXED'
            assert price_span['product_uid'] == 2
            assert price_span['pricebook_id'] == '10'
            assert price_span['contract_id'] == '180'
            assert price_span['customer_id'] == '110'
    
    def test_list_price_on_overriden_contract(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_id = '180' AND product_uid = 1 ORDER BY ended_at ASC;")
        price_spans = res.fetchdf().to_dict('records')

        # We want to make sure they exist. It's possible to override them through other changes
        assert len(price_spans) == 78
    
    def test_contract_with_null_ended_at(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.price_spans WHERE contract_uid = 21 ORDER BY started_at ASC;")
        price_spans = res.fetchdf().to_dict('records')
        print(price_spans)
        assert len(price_spans) == 13
        price_span = price_spans[0]

        assert price_span['started_at'] == datetime.datetime(2023, 1, 1)
        assert price_span['ended_at'] == datetime.datetime(2024, 1, 1)
        assert price_span['price'] == '0.01'
        assert price_span['product_type'] == 'EVENT'
        assert price_span['product_uid'] == 3
        assert price_span['contract_id'] == '240'
        assert price_span['customer_id'] == '140'


class TestPriceSpansDateRange:
    def test_base_case(self, client: Client):
        min_date, max_date = client.get_price_span_date_range(('EVENT', 'FIXED'))
        assert min_date == datetime.datetime(2021, 7, 1)
        assert max_date == datetime.datetime(2036, 1, 1)
    
    def test_specific_range(self, client: Client):
        client.set_config({'rating_range': ['2023-01-01', '2023-02-01']})
        min_date, max_date = client.get_price_span_date_range(('EVENT', 'FIXED'))
        assert min_date == datetime.datetime(2023, 1, 1)
        assert max_date == datetime.datetime(2024, 1, 1)
    
    def test_specific_range_events(self, client: Client):
        client.set_config({'rating_range': ['2023-01-01', '2023-02-01']})
        min_date, max_date = client.get_price_span_date_range(('EVENT',))
        assert min_date == datetime.datetime(2023, 1, 1)
        # Contract 21 has a 12 month contract price
        assert max_date == datetime.datetime(2024, 1, 1)