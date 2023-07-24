def convert_scientific_to_number(s): 
    try:
        return float(s)
    except ValueError:
        return s
    