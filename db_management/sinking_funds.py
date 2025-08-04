from db_management.datasource import execute_query_df, save_dataframe_to_db


def save_sinking_fund_transactions(df):
    result = save_dataframe_to_db(df, 'sinking_fund_transactions')
    return result


def get_funds_dict():
    query = "SELECT id, fund_name FROM sinking_funds ORDER BY fund_name"

    df = execute_query_df(query)

    if not df.empty:
        funds_dict = df.set_index('id').to_dict(orient='index')
        return funds_dict
    print("No sinking funds found in the database.")
    return {}

    
def get_sinking_fund_values():
    query = "SELECT s.fund_name, COALESCE(SUM(t.amount), 0) as fund_value FROM sinking_funds s LEFT JOIN sinking_fund_transactions t ON t.fund_id = s.id GROUP BY s.fund_name;"

    df = execute_query_df(query)
    
    if not df.empty:
        funds_dict = df.set_index('fund_name').to_dict(orient='index')
        return funds_dict
    print("No sinking funds found in the database.")
    return {}

def get_fund_contributions():
    query = "SELECT id, fund_name, default_contribution, contribution_category_id, cap FROM sinking_funds"

    df = execute_query_df(query)

    if not df.empty:
        fund_contributions_dict = df.set_index('fund_name').to_dict(orient='index')
        return fund_contributions_dict
    print("No sinking fund contributions found in the database.")
    return {}

def get_all_sinking_fund_transactions(month, year, fund_id):
    if fund_id != 0:
        if month > 0:
            query = f"SELECT date, description, -amount AS amount, fund_name FROM sinking_fund_transactions t JOIN sinking_funds s ON t.fund_id = s.id AND EXTRACT(MONTH FROM t.date) = {month} AND EXTRACT(YEAR FROM t.date) = {year} AND amount < 0 AND t.fund_id = {fund_id} ORDER BY t.date DESC"
        else:
            query = f"SELECT date, description, -amount AS amount, fund_name FROM sinking_fund_transactions t JOIN sinking_funds s ON t.fund_id = s.id AND EXTRACT(YEAR FROM t.date) = {year} AND amount < 0 AND t.fund_id = {fund_id} ORDER BY t.date DESC"
    else:
        if month > 0:
            query = f"SELECT date, description, -amount AS amount, fund_name FROM sinking_fund_transactions t JOIN sinking_funds s ON t.fund_id = s.id AND EXTRACT(MONTH FROM t.date) = {month} AND EXTRACT(YEAR FROM t.date) = {year} AND amount < 0 ORDER BY t.date DESC"
        else:
            query = f"SELECT date, description, -amount AS amount, fund_name FROM sinking_fund_transactions t JOIN sinking_funds s ON t.fund_id = s.id AND EXTRACT(YEAR FROM t.date) = {year} AND amount < 0 ORDER BY t.date DESC"

    df = execute_query_df(query)

    return df
