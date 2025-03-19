import numpy
import pandas as pd
import datetime
from bframelib import Client
from utils import apply_utc_on_cols

class TestPrices:
    def test_insert_price(self, client: Client):
        res = client.execute(f"INSERT INTO src.prices BY NAME (SELECT * FROM bframe.prices limit 1);")
        assert res.fetchone() == (1,)

    def test_event_price(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.prices WHERE list_price_uid = 1 and contract_uid = 1")
        price = res.fetchdf().to_dict('records')[0]
        assert price['price'] == '0.25'
        assert price['invoice_delivery'] == 'ARREARS'
        assert price['invoice_schedule'] == 1
        assert price['product_uid'] == 1
        assert price['pricebook_uid'] == 1

    def test_fixed_price(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.prices WHERE list_price_uid = 2 and contract_uid = 1;")
        price = res.fetchdf().to_dict('records')[0]
        assert price['price'] == '1000'
        assert price['invoice_delivery'] == 'ADVANCED'
        assert price['invoice_schedule'] == 12
        assert price['product_uid'] == 2
        assert price['pricebook_uid'] == 1

    def test_price_override(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.prices WHERE list_price_uid = 2 and contract_uid = 8;")
        price = res.fetchdf().to_dict('records')[0]

        assert price['price'] == '12345'
        assert price['invoice_delivery'] == 'ADVANCED'
        assert price['invoice_schedule'] == 4
        assert price['product_type'] == 'FIXED'
        assert price['product_uid'] == 2
        assert price['pricebook_uid'] == 1
    
    def test_solo_contract_price(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.prices WHERE contract_price_uid = 5;")
        prices = res.fetchdf().to_dict('records')
        assert len(prices), 1
        price = prices[0]

        assert price['price'] == '55.34'
        assert price['invoice_delivery'] == 'ADVANCED'
        assert price['invoice_schedule'] == 3
        assert price['product_type'] == 'FIXED'
        assert price['product_uid'] == 4
        assert numpy.isnan(price['pricebook_uid'])
        assert numpy.isnan(price['list_price_uid'])

    def test_contract_with_pricebook_and_ad_hoc_price(self, client: Client):
        # Test that there are 4 prices found since we are inheriting from a pricebook with 3 prices
        res = client.execute(f"SELECT * FROM bframe.prices WHERE contract_uid = 16;")
        prices = res.fetchdf().to_dict('records')
        assert len(prices), 4

        # Check the contract price is correct
        res = client.execute(f"SELECT * FROM bframe.prices WHERE contract_price_uid = 7;")
        prices = res.fetchdf().to_dict('records')
        assert len(prices), 1
        price = prices[0]

        assert price['price'] == '-100.00'
        assert price['invoice_delivery'] == 'ADVANCED'
        assert price['invoice_schedule'] == 12
        assert price['product_type'] == 'FIXED'
        assert price['product_uid'] == 4
        assert numpy.isnan(price['list_price_uid'])

    def test_price_schedule_first_half(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.prices WHERE list_price_uid = 11 and contract_uid = 10;")
        df = res.df()
        apply_utc_on_cols(df)
        # df['started_at'] = pd.to_datetime(df['started_at'], utc=True)
        # df['ended_at'] = pd.to_datetime(df['ended_at'], utc=True)

        price = df.to_dict('records')[0]
        print(price)

        assert price['price'] == '100'
        assert price['started_at'] == datetime.datetime(2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['ended_at'] == datetime.datetime(2023, 3, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['invoice_delivery'] == 'ARREARS'
        assert price['invoice_schedule'] == 1
        assert price['product_type'] == 'FIXED'
        assert price['product_uid'] == 2
        assert price['pricebook_uid'] == 5
    
    def test_price_schedule_second_half(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.prices WHERE list_price_uid = 12 and contract_uid = 10;")
        df = res.df()
        apply_utc_on_cols(df)
        price = df.to_dict('records')[0]

        assert price['price'] == '999'
        assert price['started_at'] == datetime.datetime(2023, 3, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['ended_at'] == datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['invoice_delivery'] == 'ARREARS'
        assert price['invoice_schedule'] == 1
        assert price['product_type'] == 'FIXED'
        assert price['product_uid'] == 2
        assert price['pricebook_uid'] == 5

    def test_price_cp_started_and_ended_at(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.prices WHERE contract_uid = 15;")
        df = res.df()
        apply_utc_on_cols(df)
        price = df.to_dict('records')[0]

        assert price['price'] == '-1000.00'
        assert price['started_at'] == datetime.datetime(2023, 6, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['ended_at'] == datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['invoice_delivery'] == 'ADVANCED'
        assert price['invoice_schedule'] == 12
        assert price['product_type'] == 'FIXED'
        assert price['product_uid'] == 4
    
    # This tests that when effective dates for pricebooks and contracts don't overlap additional prices are
    # not created. The seed data used in the test gives an example of how what non-overlapping is defined as
    def test_pricebook_and_contract_different_effective_dates(self, client: Client):
        res = client.execute(f"SELECT * FROM bframe.prices WHERE contract_uid = 18;")
        df = res.df()
        apply_utc_on_cols(df)
        prices = df.to_dict('records')
        assert len(prices) == 1
        price = prices[0]

        assert price['price'] == '1000.00'
        assert price['started_at'] == datetime.datetime(2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['ended_at'] == datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['invoice_delivery'] == 'ARREARS'
        assert price['invoice_schedule'] == 1
        assert price['product_type'] == 'FIXED'
        assert price['product_uid'] == 2

        res = client.execute(f"SELECT * FROM bframe.prices WHERE contract_uid = 19;")
        df = res.df()
        apply_utc_on_cols(df)
        prices = df.to_dict('records')
        assert len(prices) == 1
        price = prices[0]

        assert price['price'] == '588.99'
        assert price['started_at'] == datetime.datetime(2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['ended_at'] == datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        assert price['invoice_delivery'] == 'ARREARS'
        assert price['invoice_schedule'] == 1
        assert price['product_type'] == 'FIXED'
        assert price['product_uid'] == 2

