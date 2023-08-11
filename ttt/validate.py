from ttt.utils import convert_scientific_to_number, convert_string_to_date, convert_string_to_datestring


def validate_csv(csv_table_df):
    table_memory = csv_table_df.memory_usage(index=True).sum()
    if (table_memory > 50000000):
        raise ValueError(
            "Unfortunately your file was too large. At this point Talk to Table is limited to 50 Megabytes or less."
        )
    
    for column in csv_table_df.columns:
        print(column)
        if column.isnumeric():
            raise ValueError(
                f"It looks like your file did not contain a header line. The header '{column}' is a number. Numbers are not allowed as headers."
            )
        date_column = convert_string_to_date(column)
        if type(date_column) is not str:
            raise ValueError(
                f"It looks like your file did not contain a header line. The header '{column}' is a date. Dates are not allowed as headers."
            )


    csv_table_df.columns = csv_table_df.columns.str.replace(" ", "_")
    csv_table_df = csv_table_df.applymap(convert_scientific_to_number)
    #csv_table_df = csv_table_df.applymap(convert_string_to_date)
    csv_table_df = csv_table_df.applymap(convert_string_to_datestring)

    return csv_table_df