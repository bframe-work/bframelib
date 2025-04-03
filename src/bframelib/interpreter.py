import re
import sqlparse
from . import PATH
from pathlib import Path
from jinja2 import Template


def format_array(array: list[str], is_str: bool):
    if (array):
        if (is_str):
            str_items = "', '".join(array)
            return f"['{str_items}']"
        else:
            str_items = ", ".join(array)
            return f"[{str_items}]"
    
    return '[]'


class Interpreter:
    def add_table_template(self, name, template):
        """Add a single template to the dictionary
        
        Args:
            name (str): Name of the template
            template (str): Either a file path or SQL string
        """
        if not isinstance(name, str) or not isinstance(template, str):
            raise TypeError("Name and template must be strings")
        
        self._table_templates[name] = template

    _table_templates = {
        '_raw_branches': Path(f'{PATH}/client_sql/_raw_branches.sql').read_text(),
        '_raw_products': Path(f'{PATH}/client_sql/_raw_products.sql').read_text(),
        '_local_products': Path(f'{PATH}/client_sql/_local_products.sql').read_text(),
        'products': Path(f'{PATH}/client_sql/products.sql').read_text(),
        '_raw_customers': Path(f'{PATH}/client_sql/_raw_customers.sql').read_text(),
        '_local_customers': Path(f'{PATH}/client_sql/_local_customers.sql').read_text(),
        'customers': Path(f'{PATH}/client_sql/customers.sql').read_text(),
        '_raw_pricebooks': Path(f'{PATH}/client_sql/_raw_pricebooks.sql').read_text(),
        '_local_pricebooks': Path(f'{PATH}/client_sql/_local_pricebooks.sql').read_text(),
        'pricebooks': Path(f'{PATH}/client_sql/pricebooks.sql').read_text(),
        '_raw_list_prices': Path(f'{PATH}/client_sql/_raw_list_prices.sql').read_text(),
        '_local_list_prices': Path(f'{PATH}/client_sql/_local_list_prices.sql').read_text(),
        'list_prices': Path(f'{PATH}/client_sql/list_prices.sql').read_text(),
        '_raw_contracts': Path(f'{PATH}/client_sql/_raw_contracts.sql').read_text(),
        '_local_contracts': Path(f'{PATH}/client_sql/_local_contracts.sql').read_text(),
        'contracts': Path(f'{PATH}/client_sql/contracts.sql').read_text(),
        '_raw_contract_prices': Path(f'{PATH}/client_sql/_raw_contract_prices.sql').read_text(),
        '_local_contract_prices': Path(f'{PATH}/client_sql/_local_contract_prices.sql').read_text(),
        'contract_prices': Path(f'{PATH}/client_sql/contract_prices.sql').read_text(),
        '_raw_events': Path(f'{PATH}/client_sql/_raw_events.sql').read_text(),
        '_local_events': Path(f'{PATH}/client_sql/_local_events.sql').read_text(),
        'events': Path(f'{PATH}/client_sql/events.sql').read_text(),
        'prices': Path(f'{PATH}/client_sql/prices.sql').read_text(),
        'processed_events': Path(f'{PATH}/client_sql/processed_events.sql').read_text(),
        'matched_events': Path(f'{PATH}/client_sql/matched_events.sql').read_text(),
        '_all_price_spans': Path(f'{PATH}/client_sql/_all_price_spans.sql').read_text(),
        'price_spans': Path(f'{PATH}/client_sql/price_spans.sql').read_text(),
        'rated_events': Path(f'{PATH}/client_sql/rated_events.sql').read_text(),
        'event_line_items': Path(f'{PATH}/client_sql/event_line_items.sql').read_text(),
        'fixed_line_items': Path(f'{PATH}/client_sql/fixed_line_items.sql').read_text(),
        'line_items': Path(f'{PATH}/client_sql/line_items.sql').read_text(),
        'invoices': Path(f'{PATH}/client_sql/invoices.sql').read_text(),
        'branches': Path(f'{PATH}/client_sql/branches.sql').read_text(),
        'environments': Path(f'{PATH}/client_sql/environments.sql').read_text(),
        'organizations': Path(f'{PATH}/client_sql/organizations.sql').read_text(),
        '_product_filters': Path(f'{PATH}/client_sql/_product_filters.sql').read_text(),
        'dates': Path(f'{PATH}/client_sql/dates.sql').read_text(),
        '_all_line_items': Path(f'{PATH}/client_sql/_all_line_items.sql').read_text(),
        '_raw_invoices': Path(f'{PATH}/client_sql/_raw_invoices.sql').read_text(),
        '_raw_line_items': Path(f'{PATH}/client_sql/_raw_line_items.sql').read_text(),
    }

    # Remove comments
    def comment_replacement(self, query: str):
        # TODO we need to handle comments inside of the views
        # Also comments at the end of the file are fully breaking (need a return at the end of the file)
        return sqlparse.format(query, strip_comments=True).strip()

    def var_replacement(self, query: str, vars: dict):
        full_match = re.search(r"_BF_(\w*\b)", query)

        # No matches we return the query back
        if (full_match is None):
            return query

        new_query = query
        variable_name = full_match.group(1)
        match variable_name:
            case 'BRANCH_ID':
                new_query = re.sub(full_match.group(), str(vars.get('branch_id')), new_query)
            case 'ORG_ID':
                new_query = re.sub(full_match.group(), str(vars.get('org_id')), new_query)
            case 'ENV_ID':
                new_query = re.sub(full_match.group(), str(vars.get('env_id')), new_query)
            case 'PROD_SYSTEM_DT':
                new_query = re.sub(full_match.group(), f"'{vars.get('prod_system_dt')}'", new_query)
            case 'BRANCH_SYSTEM_DT':
                # If there is no branch system datetime just use the production system datetime
                branch_system_dt = vars.get('branch_system_dt')
                if (branch_system_dt):
                    new_query = re.sub(full_match.group(), f"'{vars.get('branch_system_dt')}'", new_query)
                else:
                    new_query = re.sub(full_match.group(), f"'{vars.get('prod_system_dt')}'", new_query)
            case 'RATING_AS_OF_DT':
                new_query = re.sub(full_match.group(), f"'{vars.get('rating_as_of_dt')}'", new_query)
            case 'DEDUP_BRANCH_EVENTS':
                new_query = re.sub(full_match.group(), str(vars.get('dedup_branch_events')), new_query)
            case 'READ_MODE':
                new_query = re.sub(full_match.group(), f"'{vars.get('read_mode')}'", new_query)
            case 'RATING_RANGE_START':
                rating_range_start = "''"
                if (len(vars.get('rating_range')) == 2):
                    rating_range_start = f"'{vars.get('rating_range')[0]}'"
                new_query = re.sub(full_match.group(), rating_range_start, new_query)
            case 'RATING_RANGE_END':
                rating_range_end = "''"
                if (len(vars.get('rating_range')) == 2):
                    rating_range_end = f"'{vars.get('rating_range')[1]}'"
                new_query = re.sub(full_match.group(), rating_range_end, new_query)
            case 'STORED_RATING_RANGE_START':
                stored_rating_range_start = "''"
                if (len(vars.get('stored_rating_range')) == 2):
                    stored_rating_range_start = f"'{vars.get('stored_rating_range')[0]}'"
                new_query = re.sub(full_match.group(), stored_rating_range_start, new_query)
            case 'STORED_RATING_RANGE_END':
                stored_rating_range_end = "''"
                if (len(vars.get('stored_rating_range')) == 2):
                    stored_rating_range_end = f"'{vars.get('stored_rating_range')[1]}'"
                new_query = re.sub(full_match.group(), stored_rating_range_end, new_query)
            case 'CONTRACT_IDS':
                new_query = re.sub(full_match.group(), format_array(vars.get('contract_ids'), True), new_query)
            case 'CUSTOMER_IDS':
                new_query = re.sub(full_match.group(), format_array(vars.get('customer_ids'), True), new_query)
            case 'PRICEBOOK_IDS':
                new_query = re.sub(full_match.group(), format_array(vars.get('pricebook_ids'), True), new_query)
            case 'PRODUCT_UIDS':
                new_query = re.sub(full_match.group(), format_array(vars.get('product_uids'), False), new_query)
            case 'BRANCH_SOURCE_EXIST':
                exists = 'false'
                if vars.get('branch_source_exists'):
                    exists = 'true'
                new_query = re.sub(full_match.group(), exists, new_query)
            case 'EVENTS_SOURCE_EXIST':
                exists = 'false'
                if vars.get('events_source_exists'):
                    exists = 'true'
                new_query = re.sub(full_match.group(), exists, new_query)
            case 'EVENTS_SOURCE_LOCAL':
                exists = 'false'
                if vars.get('events_source_local'):
                    exists = 'true'
                new_query = re.sub(full_match.group(), exists, new_query)
            case _:
                raise Exception(f"Unknown variable: {variable_name}")
        
        return self.var_replacement(new_query, vars)


    def table_replacement(self, query, count=0, verbose=False):
        if (verbose):
            full_match = re.search(r"(\n( *).*)?(bframe\.(\w*\b))", query)
            if (full_match is None):
                return query
            spaces = full_match.group(2) or ""
            schema_table = full_match.group(3)
            table = full_match.group(4)
        else:
            full_match = re.search(r"(bframe\.(\w*\b))", query)
            if (full_match is None):
                return query
            schema_table = full_match.group(1)
            table = full_match.group(2)

        # No matches we return the query back

        if table not in self._table_templates:
            raise Exception(f'An invalid table was used: {table}')
            
        table_template = self._table_templates[table]
        
        if (verbose):
            # Whenever something is placed we must tab as well to add the spaces that already existed
            white_space = "    " + spaces
            table_template = f"(\n{white_space}" + re.sub(r"\n", "\n" + white_space, table_template) + f"\n{spaces})"
        else:
            table_template = f"({table_template})"

        resolved_query = re.sub(schema_table, table_template, query, count=1)

        return self.table_replacement(resolved_query, count=(count+1), verbose=verbose)
    
    def exec(self, vars: dict, query: str, verbose=False):
        resolved_query = self.comment_replacement(query)
        resolved_query = self.table_replacement(resolved_query, verbose=verbose)
        resolved_query = self.var_replacement(resolved_query, vars)
        resolved_query = Template(resolved_query).render()
        
        if (verbose):
            print(resolved_query)

        return resolved_query

