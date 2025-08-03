from db_management.datasource import execute_query_df, save_dataframe_to_db


def save_transactions(df):
    result = save_dataframe_to_db(df, 'transactions')
    return result


def get_all_transactions(month, year):
    if month > 0:
        query = f"SELECT * FROM transactions t JOIN budget_categories c ON t.category_id = c.id AND EXTRACT(MONTH FROM t.date) = {month} AND EXTRACT(YEAR FROM t.date) = {year} ORDER BY t.date DESC"
    else:
        query = f"SELECT * FROM transactions t JOIN budget_categories c ON t.category_id = c.id AND EXTRACT(YEAR FROM t.date) = {year} ORDER BY t.date DESC"

    df = execute_query_df(query)

    return df