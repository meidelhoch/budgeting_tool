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
    

def save_income_transactions(df):
    db_engine = get_db_engine() # Get the SQLAlchemy engine

    if db_engine is None:
        print("Failed to get database engine. Cannot save data.")
        return False

    if df.empty:
        print("No data to save.")
        return True

    try:
        df.to_sql('income', con=db_engine, if_exists='append', index=False)
        
        print(f"Successfully saved {len(df)} rows into the transactions table.")
        return True
    except Exception as e:
        print(f"Error saving data to transactions table: {e}")
        # pandas.to_sql handles its own transactions, rolling back on error automatically
        return False
    
def get_all_income_transactions(month, year):
    db_engine = get_db_engine()  # Get the SQLAlchemy engine

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch monthly icome.")
        return False
    
    if month > 0:
        query = f"SELECT * FROM income WHERE EXTRACT(MONTH FROM date) = {month} AND EXTRACT(YEAR FROM date) = {year} ORDER BY date DESC"
    else:
        query = f"SELECT * FROM income WHERE EXTRACT(YEAR FROM date) = {year} ORDER BY date DESC"

    try:
        df = pd.read_sql(SQL_text(query), db_engine)

        if not df.empty:
            print("Successfully fetched income transactions. Head of DataFrame:")
            print(df.head())
            return df
        else:
            print("No income transactions found in the database.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching income transactions: {e}")
        return False
    