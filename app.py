from flask import Flask, render_template, request
from csv_cleaning import clean_apple, clean_amex
import pandas as pd
import psycopg
import os
from dotenv import load_dotenv
from db_management.transactions import save_transactions, get_all_transactions
from db_management.sinking_funds import save_sinking_fund_transactions, get_funds_dict


load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

CATEGORIES = {
    'Grocery': 'cat-grocery',
    'Dining': 'cat-dining',
    'Shopping': 'cat-shopping',
    'Transportation': 'cat-transportation',
    'Housing': 'cat-housing',
    'Entertainment': 'cat-entertainment',
    'Travel': 'cat-travel',
    'Medical': 'cat-medical',
    'Wellness': 'cat-wellness',
    'Gifts': 'cat-gifts',
    'Other': 'cat-other',
}

SINKING_FUNDS = get_funds_dict()



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

@app.route("/budget")
def budget():
    return render_template("budget.html", active_page="budget")

@app.route("/spending")
def spending():
    transactions = get_all_transactions()
    transactions["net_amount"] = transactions["amount"] - transactions["reimbursement_amount"]
    filtered_transactions = transactions[transactions["net_amount"] > 0]
    display_transactions = filtered_transactions[["date", "description", "net_amount", "category", "card"]]

    return render_template("spending.html", active_page="spending", transactions=display_transactions.to_dict(orient='records'), categories=CATEGORIES)

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
            cleaned_data["reimbursed"] = False
            cleaned_data["reimbursement_amount"] = 0
            cleaned_data["card"] = label
            cleaned_dfs.append(cleaned_data)
            print(cleaned_data)

    if cleaned_dfs:
        combined_df = pd.concat(cleaned_dfs, ignore_index=True)
        print("Combined DataFrame:")
        print(combined_df)

        return render_template("review_transactions.html", transactions=combined_df.to_dict(orient='records'), categories=CATEGORIES, sinking_funds=SINKING_FUNDS)

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
    all_transaction_rows = []
    all_sinking_fund_rows = []

    for i in range(total):
        reimbursement_amount = request.form.get(f"reimbursement_amount_{i}", 0)
        if reimbursement_amount == "":
            reimbursement_amount = 0

        reimbursement_status = request.form.get(f"reimbursed_{i}")
        if reimbursement_status == "1":
            reimbursement_status = True
        else:
            reimbursement_status = False

        sinking_fund_id = get_fund_id(request.form.get(f"sinking_fund_{i}"))
        transaction_row = {
            "date": request.form.get(f"date_{i}"),
            "description": request.form.get(f"description_{i}"),
            "amount": float(request.form.get(f"amount_{i}")),
            "category": request.form.get(f"category_{i}"),
            "reimbursed": reimbursement_status,
            "reimbursement_amount": float(reimbursement_amount),
            "sinking_fund_id": sinking_fund_id,
            "card": request.form.get(f"card_{i}")
        }
        print(transaction_row)
        all_transaction_rows.append(transaction_row)

        if sinking_fund_id is not None:
            sinking_fund_row = {
                "fund_id": sinking_fund_id,
                "date": request.form.get(f"date_{i}"),
                "description": request.form.get(f"description_{i}"),
                "amount": float(request.form.get(f"amount_{i}"))
            }
            print(sinking_fund_row)
            all_sinking_fund_rows.append(sinking_fund_row)

    if save_transactions(pd.DataFrame(all_transaction_rows)) and save_sinking_fund_transactions(pd.DataFrame(all_sinking_fund_rows)):
        return render_template("confirmation_page.html", message="Transactions saved successfully!")
    return render_template("confirmation_page.html", message="Failed to save transactions.")

def get_fund_id(fund_name):
    if fund_name in SINKING_FUNDS:
        return SINKING_FUNDS.get(fund_name)
    else:
        return None
 

    try:
        if save_transactions(transactions):
            print(f"Successfully saved {len(transactions)} transactions.")
            return True
        else:
            print("Failed to save transactions.")
            return False
    except Exception as e:
        print(f"Error saving transactions: {e}")
        return False

@app.route("/manual-entry")
def manual_entry():
    return render_template("manual_entry.html", active_page="manual_entry")


@app.route("/settings")
def settings():
    return render_template("settings.html", active_page="settings")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)