from flask import Flask, render_template, request
from csv_cleaning import clean_apple, clean_amex
import pandas as pd
import psycopg
import os
from dotenv import load_dotenv
from db_management.transactions import save_transactions


load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

CATEGORIES = ["Grocery", "Dining", "Shopping", "Transportation", "Housing", "Entertainment", "Travel", "Other"]


app = Flask(__name__)

@app.template_filter("money")
def money_format(value):
    try:
        return "${:,.2f}".format(float(value))
    except:
        return value

@app.route("/")
def home():
    return render_template("home.html", active_page="home")

@app.route("/spending")
def spending():
    return render_template("spending.html", active_page="spending")

@app.route("/income")
def income():
    return render_template("income.html", active_page="income")

@app.route("/summary")
def summary():
    return render_template("summary.html", active_page="summary")

@app.route("/upload-statements")
def upload_statements():
    return render_template("upload.html", active_page="upload")

# TODO: NEED TO ADD AN REIMBURSED AND AMOUNT REIMBURSED COLUMN TO DB
# TODO: NEED TO FIGURE OUT THE EXACT CATEGORIES TO USE

@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_files = request.files.getlist("files")
    labels = request.form.getlist("labels")

    cleaned_dfs = []

    for file, label in zip(uploaded_files, labels):
        if file and file.filename.endswith('.csv'):
            cleaned_data = clean_file(file, label)
            cleaned_data["card"] = label
            cleaned_dfs.append(cleaned_data)
            print(cleaned_data)

    if cleaned_dfs:
        combined_df = pd.concat(cleaned_dfs, ignore_index=True)
        print("Combined DataFrame:")
        print(combined_df)

        return render_template("review_transactions.html", transactions=combined_df.to_dict(orient='records'), categories=CATEGORIES)

    else:
        print("No valid files processed.")
        return pd.DataFrame()

def clean_file(file, label):
    if label == "Apple":
        return clean_apple(file)
    elif label in ["Delta", "BlueCash"]:
        return clean_amex(file)
    else:
        raise ValueError(f"Unknown label: {label}")
    
@app.route("/save-transactions", methods=["POST"])
def save_transactions_route():
    print(request.form)
    total = int(request.form.get("total_rows", 0))
    updated_rows = []

    for i in range(total):
        row = {
            "date": request.form.get(f"date_{i}"),
            "description": request.form.get(f"description_{i}"),
            "amount": float(request.form.get(f"amount_{i}")),
            "category": request.form.get(f"category_{i}"),
            "card": request.form.get(f"card_{i}")
        }
        updated_rows.append(row)

    save_transactions(pd.DataFrame(updated_rows))

    return render_template("confirmation_page.html")


@app.route("/settings")
def settings():
    return render_template("settings.html", active_page="settings")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)