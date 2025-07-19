from db_management.datasource import get_db_engine
import pandas as pd
from sqlalchemy.sql import text as SQL_text


def save_transactions(df):
    db_engine = get_db_engine()

    if db_engine is None:
        print("Failed to get database engine. Cannot save data.")
        return False

    if df.empty:
        print("No data to save.")
        return True

    try:
        df.to_sql('transactions', con=db_engine, if_exists='append', index=False)
        
        print(f"Successfully saved {len(df)} rows into the transactions table.")
        return True
    except Exception as e:
        print(f"Error saving data to transactions table: {e}")
        return False


def get_all_transactions():
    db_engine = get_db_engine() 

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch transactions.")
        return pd.DataFrame()

    query = "SELECT * FROM transactions t JOIN budget_categories c ON t.category_id = c.id ORDER BY t.date DESC"

    try:
        df = pd.read_sql(SQL_text(query), db_engine)
        print(df)
        
        if not df.empty:
            print("Successfully fetched transactions. Head of DataFrame:")
            print(df.head())
        else:
            print("No transactions found in the database.")
            
        return df
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return pd.DataFrame() 