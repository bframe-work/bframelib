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
