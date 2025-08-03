from db_management.datasource import execute_query_df
import pandas as pd
from sqlalchemy.sql import text as SQL_text


def get_categories_dict():
    query = "SELECT id, category_name, monthly_budget, css_class FROM budget_categories ORDER BY id"

    df = execute_query_df(query)

    if not df.empty:
        categories_dict = df.set_index('id').to_dict(orient='index')
        return categories_dict
    return {}
    
def get_category_map():

    query = "SELECT id, category_name FROM budget_categories ORDER BY id"

    df = execute_query_df(query)

    if not df.empty:
        category_map = df.set_index('category_name')['id'].to_dict()
        return category_map
    return {}


def get_monthly_spending(month, year):
    query = f"SELECT c.id, category_name, COALESCE(SUM(CASE WHEN t.amount > 0 AND t.sinking_fund_id IS NULL THEN CASE WHEN t.reimbursed THEN t.amount - t.reimbursement_amount ELSE t.amount END ELSE 0 END), 0) as total_spent, monthly_budget FROM budget_categories c LEFT JOIN transactions t ON t.category_id = c.id AND EXTRACT(MONTH FROM t.date) = {month} AND EXTRACT(YEAR FROM t.date) = {year} GROUP BY category_name, monthly_budget, c.id ORDER BY c.id"

    df = execute_query_df(query)

    if not df.empty:
        total_spent = df.set_index('category_name').to_dict(orient='index')
        return total_spent
    return {}