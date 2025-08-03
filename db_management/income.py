from db_management.datasource import execute_query_df, save_dataframe_to_db


def get_monthly_income(month, year):
    query = f"SELECT COALESCE(SUM(amount), 0) as total_income FROM income WHERE EXTRACT(MONTH FROM date) = {month} AND EXTRACT(YEAR FROM date) = {year}"

    df = execute_query_df(query)

    if df.empty:
        print("No income transactions found for the specified month and year.")
        return {}
    else:
        total_income = df.at[0, 'total_income']
        print(f"Total income for {month}/{year}: {total_income}")
    return total_income


def save_income_transactions(df):
    result = save_dataframe_to_db(df, 'income')
    return result
    
def get_all_income_transactions(month, year):
    if month > 0:
        query = f"SELECT * FROM income WHERE EXTRACT(MONTH FROM date) = {month} AND EXTRACT(YEAR FROM date) = {year} ORDER BY date DESC"
    else:
        query = f"SELECT * FROM income WHERE EXTRACT(YEAR FROM date) = {year} ORDER BY date DESC"

    df = execute_query_df(query)

    return df
