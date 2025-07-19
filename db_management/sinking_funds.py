from db_management.datasource import get_db_engine
import pandas as pd
from sqlalchemy.sql import text as SQL_text

def save_sinking_fund_transactions(df):
    db_engine = get_db_engine() 

    if db_engine is None:
        print("Failed to get database engine. Cannot save data.")
        return False

    if df.empty:
        print("No data to save.")
        return True

    try:
        df.to_sql('sinking_fund_transactions', con=db_engine, if_exists='append', index=False)

        print(f"Successfully saved {len(df)} rows into the sinking_fund_transactions table.")
        return True
    except Exception as e:
        print(f"Error saving data to sinking_fund_transactions table: {e}")
        return False
    

def get_funds_dict():
    db_engine = get_db_engine() 

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch funds.")
        return {}

    query = "SELECT id, fund_name FROM sinking_funds ORDER BY fund_name"

    try:
        df = pd.read_sql(SQL_text(query), db_engine)
        
        if not df.empty:
            funds_dict = df.set_index('fund_name').to_dict(orient='index')

            print("Successfully fetched sinking funds. Funds dictionary:")
            print(funds_dict)
            return funds_dict
        else:
            print("No sinking funds found in the database.")
            return {}
    except Exception as e:
        print(f"Error fetching sinking funds: {e}")
        return {}  
    
def get_sinking_fund_values():
    db_engine = get_db_engine()  

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch sinking fund values.")
        return {}

    query = "SELECT s.fund_name, COALESCE(SUM(t.amount), 0) as fund_value FROM sinking_funds s LEFT JOIN sinking_fund_transactions t ON t.fund_id = s.id GROUP BY s.fund_name;"

    try:
        df = pd.read_sql(SQL_text(query), db_engine)

        if not df.empty:
            funds_dict = df.set_index('fund_name').to_dict(orient='index')
            print("Successfully fetched sinking fund values. Sinking funds dictionary:")
            print(funds_dict)
            return funds_dict
        else:
            print("No sinking funds found in the database.")
            return {}
    except Exception as e:
        print(f"Error fetching sinking fund values: {e}")
        return {}

def get_fund_contributions():
    db_engine = get_db_engine()  

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch sinking fund values.")
        return {}

    query = "SELECT id, fund_name, default_contribution, contribution_category_id FROM sinking_funds"

    try:
        df = pd.read_sql(SQL_text(query), db_engine)

        if not df.empty:
            fund_contributions_dict = df.set_index('fund_name').to_dict(orient='index')
            print("Successfully fetched sinking fund contributions. Sinking fund contributions dictionary:")
            print(fund_contributions_dict)
            return fund_contributions_dict
        else:
            print("No sinking funds found in the database.")
            return {}
    except Exception as e:
        print(f"Error fetching sinking fund values: {e}")
        return {}  

def get_all_sinking_fund_transactions(month, year):
    db_engine = get_db_engine()  

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch sinking fund values.")
        return pd.DataFrame()
    
    if month > 0:
        query = f"SELECT date, description, -amount AS amount, fund_name FROM sinking_fund_transactions t JOIN sinking_funds s ON t.fund_id = s.id AND EXTRACT(MONTH FROM t.date) = {month} AND EXTRACT(YEAR FROM t.date) = {year} AND amount < 0 ORDER BY t.date DESC"
    else:
        query = f"SELECT date, description, -amount AS amount, fund_name FROM sinking_fund_transactions t JOIN sinking_funds s ON t.fund_id = s.id AND EXTRACT(YEAR FROM t.date) = {year} AND amount < 0 ORDER BY t.date DESC"


    try:
        df = pd.read_sql(SQL_text(query), db_engine)
        print(df)

        if not df.empty:
            print("Successfully fetched sinking fund transactions. Sinking funds dictionary:")
            return df
        else:
            print("No sinking funds found in the database.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching sinking fund values: {e}")
        return pd.DataFrame()