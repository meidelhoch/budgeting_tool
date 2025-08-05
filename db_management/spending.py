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

def get_monthly_spending_by_category(year):
    query = f"""
    SELECT
        EXTRACT(MONTH FROM t.date) AS month,
        c.category_name AS category,
        COALESCE(SUM(CASE WHEN t.amount > 0 AND t.sinking_fund_id IS NULL THEN CASE WHEN t.reimbursed THEN t.amount - t.reimbursement_amount ELSE t.amount END ELSE 0 END), 0) as total_spent
    FROM transactions t
    JOIN budget_categories c ON t.category_id = c.id
    WHERE EXTRACT(YEAR FROM t.date) = {year}
    GROUP BY month, c.category_name
    ORDER BY month, c.category_name;
    """
    
    df = execute_query_df(query)
    
    return df

def get_daily_spending_by_category(month, year):
    query = f"""
    SELECT
        EXTRACT(DAY FROM t.date) AS day,
        c.category_name AS category,
        COALESCE(SUM(CASE WHEN t.amount > 0 AND t.sinking_fund_id IS NULL THEN CASE WHEN t.reimbursed THEN t.amount - t.reimbursement_amount ELSE t.amount END ELSE 0 END), 0) as total_spent
    FROM transactions t
    JOIN budget_categories c ON t.category_id = c.id
    WHERE EXTRACT(MONTH FROM t.date) = {month} AND EXTRACT(YEAR FROM t.date) = {year}
    AND t.description NOT ILIKE '%sinking fund contribution%'
    AND t.description NOT ILIKE '%rent payment%'
    GROUP BY day, c.category_name
    ORDER BY day, c.category_name;
    """
    
    df = execute_query_df(query)
    
    return df