from bframelib import Client

class TestDateRange:
    def test_base_case(self, client: Client):
        dates = client.execute("""
            select *
            from bframe.dates
            where month_start between '2023-01-01' and '2023-12-01';
        """).fetchall()

        assert len(dates) == 12

    def test_limit_range(self, client: Client):
        client.set_config({'rating_range': ['2023-01-01', '2023-07-01']})
        dates = client.execute("""
            select *
            from bframe.dates
            where month_start between '2023-01-01' and '2023-12-01';
        """).fetchall()

        assert len(dates) == 6

    def test_date_range_smaller_than_a_month(self, client: Client):
        client.set_config({'rating_range': ['2023-01-02', '2023-02-01']})
        dates = client.execute("""
            select *
            from bframe.dates
            where month_start between '2023-01-01' and '2023-12-01';
        """).fetchall()

        assert len(dates) == 1