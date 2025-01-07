# Initially I looked into how to unpack dictionaries a bit more cleanly, but the sqlite3 library doesn't have anything to solve this case
# The recommendation is to use the sqlite string argument interpolation, and not string interpolation due to risk of sql injection
# since these are just tests, we think it's fine to just do string interpolation during INSERTs. This significantly cleans up our code by
# doing things with string interpolation and the tradeoff is we end up using this in production later on. I'm not too worried about that since
# since we don't plan on using sqlite in production in the first place.
def field_value_tuple(obj_dict):
    fields, values = zip(*obj_dict.items())
    str_values = []
    for value in values:
        if value == None:
            str_values.append('NULL')
        else:
            str_values.append(str(value))
    return (str(fields).replace("'", ""), tuple(str_values))