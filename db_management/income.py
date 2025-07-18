from db_management.datasource import get_db_engine
import pandas as pd
from sqlalchemy.sql import text as SQL_text

def get_monthly_income(month, year):
    db_engine = get_db_engine()  # Get the SQLAlchemy engine

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch monthly icome.")
        return {}

    query = f"SELECT COALESCE(SUM(amount), 0) as total_income FROM income WHERE EXTRACT(MONTH FROM date) = {month} AND EXTRACT(YEAR FROM date) = {year}"
    try:
        df = pd.read_sql(SQL_text(query), db_engine)

        if not df.empty:
            total_income = df.iloc[0]['total_income']
            print("Successfully fetched total income. Total income dictionary:")
            print(total_income)
            return total_income
        else:
            print("No transactions found in the database.")
            return {}
    except Exception as e:
        print(f"Error fetching total income: {e}")
        return {}  # Return empty dict on error