from bframelib import Client

class TestInterpreter:
    def test_line_comments(self, client: Client):
        commented_query = """
            -- select * from bframe.invoices;
            SELECT * FROM bframe.customers WHERE id = 2; -- this is a comment about bframe.customers
        """
        no_comment_query = "SELECT * FROM bframe.customers WHERE id = 2;"
        interpreted_comment_query = client.interpreter.exec(client.config, commented_query)
        interpreted_query = client.interpreter.exec(client.config, no_comment_query)

        
        assert interpreted_query == interpreted_comment_query
    
    def test_block_comments(self, client: Client):
        commented_query = """
            /* select * from bframe.invoices; */
            SELECT * FROM bframe.customers WHERE id = 2; /* peekaboo */
        """
        no_comment_query = "SELECT * FROM bframe.customers WHERE id = 2;"
        interpreted_comment_query = client.interpreter.exec(client.config, commented_query)
        interpreted_query = client.interpreter.exec(client.config, no_comment_query)

        
        assert interpreted_query == interpreted_comment_query

    def test_add_table_template(self, client: Client):
        client.interpreter.add_table_template('test_table', 'SELECT 1 AS one, 2 AS two')
        res = client.execute('SELECT one, two FROM bframe.test_table;')
        assert res.fetchone() == (1, 2)

    def test_unicode_in_contract_ids(self, client: Client):
        contract_id = 'André Verheye_contract'
        client.set_config({'contract_ids': [contract_id]})
        try:
            client.execute(f"SELECT * FROM bframe.contracts WHERE durable_id = '{contract_id}';")
            assert True
        except Exception as e:
            print(e)
            assert False

    def test_contract_id_filter(self, client: Client):
        client.set_config({'contract_ids': ['130']})
        res = client.execute(f"SELECT * FROM bframe.contracts;")
        
        contracts = res.fetchdf().to_dict('records')

        # Ensure only gets contracts associated with the durable key set
        assert len(contracts) == 1
        assert contracts[0]['durable_id'] == '130'

        client.set_config({
            'contract_ids': [],
            'customer_ids': [contracts[0]['customer_id']]
        })

        res = client.execute(f"SELECT * FROM bframe.contracts;")
        
        contracts = res.fetchdf().to_dict('records')

        # Ensure only gets contracts associated with the customer id are pulled
        assert len(contracts) == 1
        assert contracts[0]['durable_id'] == '130'

        client.set_config({
            'branch_id': 2,
        })

        res = client.execute(f"SELECT * FROM bframe.contracts;")
        
        contracts = res.fetchdf().to_dict('records')

        # Ensure only gets contracts associated with the customer id are pulled, even on a different branch
        assert len(contracts) == 1
        assert contracts[0]['durable_id'] == '130'

    def test_customer_id_filter(self, client: Client):
        client.set_config({'customer_ids': ['30']})
        res = client.execute(f"SELECT * FROM bframe.customers;")
        
        customers = res.fetchdf().to_dict('records')

        # Ensure only gets customers associated with the durable key set
        assert len(customers) == 1
        assert customers[0]['durable_id'] == '30'

        res = client.execute(f"SELECT * FROM bframe.events;")
        
        events = res.fetchdf().to_dict('records')

        # Ensure only gets events associated with the customer
        assert len(events) == 2
        assert events[0]['customer_id'] == '30'
        assert events[1]['customer_id'] == '30'

        client.set_config({
            'branch_id': 2,
        })

        res = client.execute(f"SELECT * FROM bframe.customers;")
        
        customers = res.fetchdf().to_dict('records')

        # Ensure only gets customers associated with the customer id are pulled, even on a different branch
        assert len(customers) == 1
        assert customers[0]['durable_id'] == '30'

    def test_product_uid_filter(self, client: Client):
        client.set_config({'product_uids': ['1']})
        res = client.execute(f"SELECT * FROM bframe.products;")
        
        products = res.fetchdf().to_dict('records')

        # Ensure only gets products associated with the id set
        assert len(products) == 1
        assert products[0]['id'] == 1

        client.set_config({
            'branch_id': 2,
        })

        res = client.execute(f"SELECT * FROM bframe.products;")
        
        products = res.fetchdf().to_dict('records')

        # Ensure local products are also filtered
        assert len(products) == 1
        assert products[0]['id'] == 1
    
    def test_pricebook_id_filter(self, client: Client):
        client.set_config({'pricebook_ids': ['20']})
        res = client.execute(f"SELECT * FROM bframe.pricebooks;")
        
        pricebooks = res.fetchdf().to_dict('records')

        # Ensure only gets pricebooks associated with the id set
        assert len(pricebooks) == 1
        assert pricebooks[0]['id'] == 2

    


        
