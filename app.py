from flask import Flask, render_template, request
from csv_cleaning import clean_apple, clean_amex
import pandas as pd
import psycopg
import os
from dotenv import load_dotenv


load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_files = request.files.getlist("files")
    labels = request.form.getlist("labels")

    cleaned_dfs = []

    for file, label in zip(uploaded_files, labels):
        if file and file.filename.endswith('.csv'):
            print(f"Received file: {file.filename}")
            if label == "Apple":
                cleaned_data = clean_apple(file)
                print(f"Cleaned Apple Card Data:\n{cleaned_data}")
            elif label == "Delta" or label == "BlueCash":
                cleaned_data = clean_amex(file)
                print(f"Cleaned Amex Card Data:\n{cleaned_data}")
            else:
                print(f"Unknown label: {label}")

            cleaned_data["Card"] = label

            cleaned_dfs.append(cleaned_data)

    if cleaned_dfs:
        # Combine all cleaned DataFrames into one
        combined_df = pd.concat(cleaned_dfs, ignore_index=True)
        print(f"Combined Cleaned Data:\n{combined_df}")

        # Prepare data as list of tuples from your DataFrame
        data = [tuple(row) for row in combined_df.itertuples(index=False)]

        # Build insert query with placeholders
        placeholders = ', '.join(['%s'] * len(combined_df.columns))
        query = f"INSERT INTO transactions ({', '.join(combined_df.columns)}) VALUES ({placeholders})"

        with psycopg.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        ) as conn:
            with conn.cursor() as cur:
                # Execute the insert query with the data
                cur.executemany(query, data)
                conn.commit()

        # Return a JSON summary or success message instead of DataFrame
        return {"status": "success", "rows_inserted": len(combined_df)}

    else:
        print("No valid files processed.")
        return pd.DataFrame()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)