import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import text as SQL_text
import pandas as pd

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

engine = None

def get_db_engine():
    global engine
    if engine is not None:
        return engine

    try:
        database_url = (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@"
            f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as connection:
            connection.execute(SQL_text("SELECT 1"))
            print("Successfully connected to the database via SQLAlchemy!")
            
        return engine

    except Exception as e:
        print(f"Error creating SQLAlchemy engine or connecting to the database: {e}")
        raise

def execute_query_df(query):
    db_engine = get_db_engine() 

    if db_engine is None:
        print("Failed to get database engine. Cannot fetch data.")
        return pd.DataFrame()
    
    try:
        df = pd.read_sql(SQL_text(query), db_engine)
        print(df)
        
        if not df.empty:
            print("Successfully fetched data. Head of DataFrame:")
            print(df.head())
        else:
            print("No data found in the database.")

        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def save_dataframe_to_db(df, table_name):
    db_engine = get_db_engine() # Get the SQLAlchemy engine

    if db_engine is None:
        print("Failed to get database engine. Cannot save data.")
        return False

    if df.empty:
        print("No data to save.")
        return True

    try:
        df.to_sql(table_name, con=db_engine, if_exists='append', index=False)

        print(f"Successfully saved {len(df)} rows into the {table_name} table.")
        return True
    except Exception as e:
        print(f"Error saving data to {table_name} table: {e}")
        return False
    
def delete_all_data_from_db():
    db_engine = get_db_engine()  # Get the SQLAlchemy engine

    if db_engine is None:
        print("Failed to get database engine. Cannot delete data.")
        return False

    try:
        with db_engine.begin() as connection:
            connection.execute(SQL_text("TRUNCATE TABLE transactions, income, sinking_fund_transactions RESTART IDENTITY CASCADE"))
            print("All data has been deleted from the database.")
        return True
    except Exception as e:
        print(f"Error deleting data: {e}")
        return False