from db_management.datasource import get_db_engine
import pandas as pd
from sqlalchemy.sql import text as SQL_text


def get_categories_dict():
    db_engine = get_db_engine()  # Get the SQLAlchemy engine

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch categories.")
        return {}

    query = "SELECT id, category_name, monthly_budget, css_class FROM budget_categories ORDER BY id"

    try:
        df = pd.read_sql(SQL_text(query), db_engine)

        if not df.empty:
            categories_dict = df.set_index('category_name').to_dict(orient='index')
            print("Successfully fetched budget categories. Categories dictionary:")
            print(categories_dict)
            return categories_dict
        else:
            print("No budget categories found in the database.")
            return {}
    except Exception as e:
        print(f"Error fetching budget categories: {e}")
        return {}  # Return empty dict on error

def get_monthly_spending(month, year):
    db_engine = get_db_engine()  # Get the SQLAlchemy engine

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch monthly spending.")
        return {}

    query = f"SELECT c.id, category_name, COALESCE(SUM(t.amount), 0) as total_spent, monthly_budget FROM budget_categories c LEFT JOIN transactions t ON t.category_id = c.id AND EXTRACT(MONTH FROM t.date) = {month} AND EXTRACT(YEAR FROM t.date) = {year} GROUP BY category_name, monthly_budget, c.id ORDER BY c.id"

    try:
        df = pd.read_sql(SQL_text(query), db_engine)

        if not df.empty:
            total_spent = df.set_index('category_name').to_dict(orient='index')
            print("Successfully fetched total spent. Total spent dictionary:")
            print(total_spent)
            return total_spent
        else:
            print("No transactions found in the database.")
            return {}
    except Exception as e:
        print(f"Error fetching total spent: {e}")
        return {}  # Return empty dict on error

