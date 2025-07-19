from flask import Flask, render_template, request
from csv_cleaning import clean_apple, clean_amex
import pandas as pd
import psycopg
import os
from datetime import datetime
import calendar
from dotenv import load_dotenv
from db_management.transactions import save_transactions, get_all_transactions
from db_management.sinking_funds import save_sinking_fund_transactions, get_funds_dict, get_sinking_fund_values
from db_management.budget import get_categories_dict, get_monthly_spending
from db_management.income import get_monthly_income, save_income_transactions


load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

CATEGORIES = get_categories_dict()

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
    now = datetime.now()
    month = int(request.args.get("month", now.month - 1 if now.month > 1 else 12))  # Default to last month, but if January, go to December
    year = int(request.args.get("year", now.year))
    current_year = now.year
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    monthly_spending = get_monthly_spending(month, year)
    sinking_fund_values = get_sinking_fund_values()
    total_spent_sum = sum((data['total_spent'] for data in monthly_spending.values()), 0)
    total_budget_sum = sum((data['monthly_budget'] for data in monthly_spending.values()), 0)

    monthly_income = get_monthly_income(month, year)
    return render_template("budget.html", active_page="budget", monthly_income=monthly_income, total_spent=total_spent_sum, total_budget=total_budget_sum, monthly_spending=monthly_spending, current_year=current_year, selected_month=month, selected_year=year, months=months, sinking_fund_values=sinking_fund_values)


@app.route("/spending")
def spending():
    transactions = get_all_transactions()
    transactions["net_amount"] = transactions["amount"] - transactions["reimbursement_amount"]
    filtered_transactions = transactions[transactions["net_amount"] > 0]
    display_transactions = filtered_transactions[["date", "description", "net_amount", "category_name", "payment_method"]]

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
            cleaned_data["payment_method"] = label
            cleaned_dfs.append(cleaned_data)

    if cleaned_dfs:
        combined_df = pd.concat(cleaned_dfs, ignore_index=True)

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
    total = int(request.form.get("total_rows", 0))
    all_transaction_rows = []
    all_sinking_fund_rows = []

    for i in range(total):
        reimbursement_amount = get_reimbursement_amount(request.form.get(f"reimbursement_amount_{i}", 0))
        reimbursement_status = get_reimbursement_status(request.form.get(f"reimbursed_{i}"))
        sinking_fund_id = get_fund_id(request.form.get(f"sinking_fund_{i}"))

        transaction_row = {
            "date": request.form.get(f"date_{i}"),
            "description": request.form.get(f"description_{i}"),
            "amount": float(request.form.get(f"amount_{i}")),
            "category_id": get_category_id(request.form.get(f"category_{i}")),
            "reimbursed": reimbursement_status,
            "reimbursement_amount": float(reimbursement_amount),
            "sinking_fund_id": sinking_fund_id,
            "payment_method": request.form.get(f"payment_method_{i}")
        }

        all_transaction_rows.append(transaction_row)

        if sinking_fund_id is not None:
            sinking_fund_row = {
                "fund_id": sinking_fund_id,
                "date": request.form.get(f"date_{i}"),
                "description": request.form.get(f"description_{i}"),
                "amount": -float(request.form.get(f"amount_{i}"))
            }
            all_sinking_fund_rows.append(sinking_fund_row)

    if save_transactions(pd.DataFrame(all_transaction_rows)) and save_sinking_fund_transactions(pd.DataFrame(all_sinking_fund_rows)):
        return render_template("confirmation_page.html", message="Transactions saved successfully!")
    return render_template("confirmation_page.html", message="Failed to save transactions.")


def get_reimbursement_amount(raw_reimbursement_amount):
    if raw_reimbursement_amount == "":
        return 0
    return raw_reimbursement_amount


def get_reimbursement_status(raw_reimbursement_status):
    if raw_reimbursement_status == 1:
        return True
    return False


def get_fund_id(fund_name):
    if fund_name in SINKING_FUNDS:
        return SINKING_FUNDS.get(fund_name)
    else:
        return None


def get_category_id(category):
    id = CATEGORIES.get(category).get("id")
    return id


@app.route("/manual-entry")
def manual_entry():
    return render_template("manual_entry.html", active_page="manual_entry", categories=CATEGORIES)


@app.route("/manual-entry-spending", methods=["POST"])
def manual_entry_spending():
    num_entries = int(request.form.get("spending_num_entries", 0))
    row_list = []

    for i in range(num_entries):
        date = request.form.get(f"transaction_date[{i}]")
        description = request.form.get(f"description[{i}]")
        amount = request.form.get(f"amount[{i}]")
        category = request.form.get(f"category[{i}]")
        payment_method = request.form.get(f"payment_method[{i}]")

        new_row = {
            "date": date,
            "description": description,
            "amount": float(amount) if amount else 0.0,
            "category": category,
            "payment_method": payment_method, 
            "reimbursed": False,
            "reimbursement_amount": 0,
        }

        row_list.append(new_row)

        df = pd.DataFrame(row_list)

    return render_template("review_transactions.html", transactions=df.to_dict(orient='records'), categories=CATEGORIES, sinking_funds=SINKING_FUNDS)


@app.route("/manual-entry-income", methods=["POST"])
def manual_entry_income():
    print(request.form)
    num_entries = int(request.form.get("income_num_entries", 0))
    row_list = []

    for i in range(num_entries):
        date = request.form.get(f"income_date[{i}]")
        description = request.form.get(f"description[{i}]")
        amount = request.form.get(f"amount[{i}]")

        new_row = {
            "date": date,
            "description": description,
            "amount": float(amount) if amount else 0.0,
        }

        row_list.append(new_row)
        print(new_row)

        df = pd.DataFrame(row_list)

    if save_income_transactions(df):
        return render_template("confirmation_page.html", message="Income transactions saved successfully")
    return render_template("confirmation_page.html", message="Failed to save income transactions")
    

@app.route("/settings")
def settings():
    return render_template("settings.html", active_page="settings")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)