from db_management.datasource import get_db_connection

def save_transactions(df):
    with get_db_connection() as conn:
        if conn is None:
            print("Failed to connect to the database.")
            return False
        
        if df.empty:
            print("No data to save.")
            return False
        
        with conn.cursor() as cursor:
            # Build insert query with placeholders
            data = [tuple(row) for row in df.itertuples(index=False)]


            placeholders = ', '.join(['%s'] * len(df.columns))
            query = f"INSERT INTO transactions ({', '.join(df.columns)}) VALUES ({placeholders})"
            
            try:
                cursor.executemany(query, data)
                conn.commit()
                print(f"Inserted {cursor.rowcount} rows into the transactions table.")
                return True
            except Exception as e:
                print(f"Error inserting data: {e}")
                conn.rollback()
                return False
