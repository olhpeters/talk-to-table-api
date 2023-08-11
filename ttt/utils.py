from dateutil.parser import parse, ParserError

def convert_scientific_to_number(s): 
    try:
        return float(s)
    except ValueError:
        return s

def convert_string_to_date(s):
    try:
        return parse(s)
    except (ParserError, TypeError):
        return s
    
def convert_string_to_datestring(s):
    try:
        column_date=parse(s)
        return column_date.strftime("%Y-%m-%d")
    except (ParserError, TypeError):
        return s