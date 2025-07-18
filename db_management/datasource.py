import os
import psycopg
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

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
            connection.execute(text("SELECT 1"))
            print("Successfully connected to the database via SQLAlchemy!")
            
        return engine

    except Exception as e:
        print(f"Error creating SQLAlchemy engine or connecting to the database: {e}")
        raise

