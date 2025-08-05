from flask import Flask, render_template, request, redirect, url_for
from csv_cleaning import clean_apple, clean_amex
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import calendar
from dotenv import load_dotenv
from db_management.datasource import delete_all_data_from_db
from db_management.spending import save_transactions, get_all_transactions, get_monthly_spending_by_category, get_daily_spending_by_category
from db_management.sinking_funds import save_sinking_fund_transactions, get_funds_dict, get_sinking_fund_values, get_fund_contributions, get_all_sinking_fund_transactions
from db_management.budget import get_categories_dict, get_monthly_spending
from db_management.income import get_monthly_income, save_income_transactions, get_all_income_transactions


load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

CATEGORIES = get_categories_dict()

SINKING_FUNDS = get_funds_dict()

PAYMENT_METHODS = ["Venmo", "Cash", "Direct Deposit", "Transfer", "Delta", "BlueCash",
                   "Apple", "Costco", "Other"]

MONTHS = [(i, calendar.month_name[i]) for i in range(1, 13)]

COLOR_MAP = {'Shopping': '#ffb374', 'Medical': '#b06464', 'Dining': '#ff9fc2', 'Transportation': '#fff895', 'Housing': '#b5fead', 'Wellness': '#69a864', 'Travel': '#A3E7F7', 'Grocery': '#5e9ef1', 'Entertainment': '#e9d1ff', 'Gifts': '#8a76b0', 'Other': '#b2b2b2'}


app = Flask(__name__)

@app.template_filter("money")
def money_format(value):
    try:
        return "${:,.2f}".format(float(value))
    except:
        return value
    

@app.route("/")
def home():
    return redirect(url_for('budget'))

@app.route("/budget")
def budget():
    now = datetime.now()
    month = int(request.args.get("month", now.month - 1 if now.month > 1 else 12))  # Default to last month, but if January, go to December
    year = int(request.args.get("year", now.year))
    current_year = now.year

    monthly_spending = get_monthly_spending(month, year)
    sinking_fund_values = get_sinking_fund_values()
    total_spent_sum = sum((data['total_spent'] for data in monthly_spending.values()), 0)
    total_budget_sum = sum((data['monthly_budget'] for data in monthly_spending.values()), 0)

    monthly_income = get_monthly_income(month, year)
    return render_template("budget.html",
                           active_page="budget",
                           monthly_income=monthly_income,
                           total_spent=total_spent_sum,
                           total_budget=total_budget_sum,
                           monthly_spending=monthly_spending,
                           current_year=current_year,
                           selected_month=month,
                           selected_year=year,
                           months=MONTHS,
                           sinking_fund_values=sinking_fund_values
                           )


@app.route("/spending")
def spending():
    now = datetime.now()
    month = int(request.args.get("month", now.month - 1 if now.month > 1 else 12))  # Default to last month, but if January, go to December
    year = int(request.args.get("year", now.year))
    current_year = now.year

    transactions = get_all_transactions(month, year)
    if not transactions.empty:
        transactions["net_amount"] = transactions["amount"] - transactions["reimbursement_amount"]
        filtered_transactions = transactions[transactions["net_amount"] > 0]
        display_transactions = filtered_transactions[["date", "description", "net_amount", "category_id", "payment_method"]]

        return render_template("spending.html",
                               active_page="spending",
                               transactions=display_transactions.to_dict(orient='records'),
                               categories=CATEGORIES,
                               current_year=current_year,
                               selected_month=month,
                               selected_year=year,
                               months=MONTHS
                               )
    return render_template("spending.html",
                           active_page="spending",
                           transactions=None,
                           categories=CATEGORIES,
                           current_year=current_year,
                           selected_month=month,
                           selected_year=year,
                           months=MONTHS
                           )


@app.route("/income")
def income():
    now = datetime.now()
    month = int(request.args.get("month", now.month - 1 if now.month > 1 else 12))  # Default to last month, but if January, go to December
    year = int(request.args.get("year", now.year))
    current_year = now.year

    transactions = get_all_income_transactions(month, year)

    if not transactions.empty:
        transactions.drop('id', axis=1, inplace=True) #remove id column
        return render_template("income.html",
                               active_page="income",
                               transactions=transactions.to_dict(orient='records'),
                               current_year=current_year,
                               selected_month=month,
                               selected_year=year,
                               months=MONTHS
                               )
    return render_template("income.html",
                           active_page="income",
                           transactions=None,
                           current_year=current_year,
                           selected_month=month,
                           selected_year=year,
                           months=MONTHS
                           )
 
@app.route("/sinking-funds")
def sinking_funds():
    print(request.args)
    now = datetime.now()
    month = int(request.args.get("month", 0))
    year = int(request.args.get("year", now.year))
    selected_fund = int(request.args.get("fund", 0))
    current_year = now.year

    print(selected_fund)

    all_transactions = get_all_sinking_fund_transactions(month, year, selected_fund)

    if not all_transactions.empty:
        return render_template("sinking_funds.html",
                               active_page="sinking_funds",
                               transactions=all_transactions.to_dict(orient='records'),
                               current_year=current_year,
                               selected_month=month,
                               selected_year=year,
                               months=MONTHS,
                               sinking_funds=SINKING_FUNDS,
                               selected_fund=selected_fund
                               )
    return render_template("sinking_funds.html",
                           active_page="sinking_funds",
                           transactions=None,
                           current_year=current_year,
                           selected_month=month,
                           selected_year=year,
                           months=MONTHS,
                           sinking_funds=SINKING_FUNDS,
                           selected_fund=selected_fund
                           )
    


@app.route("/monthly-summary")
def monthly_summary():
    now = datetime.now()
    month = int(request.args.get("month", now.month - 1 if now.month > 1 else 12))  # Default to last month, but if January, go to December
    year = int(request.args.get("year", now.year))
    current_year = now.year

    monthly_spending_by_category = get_monthly_spending(month, year)
    monthly_spending_by_category_df = pd.DataFrame.from_dict(monthly_spending_by_category, orient='index')
    monthly_spending_by_category_df.index.name = 'Category'
    monthly_spending_by_category_df.reset_index(inplace=True)
    monthly_spending_by_category_df['percent_of_budget'] = (monthly_spending_by_category_df['total_spent'] / monthly_spending_by_category_df['monthly_budget']) * 100
    print(monthly_spending_by_category_df)

    donut_chart = px.pie(monthly_spending_by_category_df, 
                         names='Category',
                         values='total_spent',
                         color='Category',
                         color_discrete_map=COLOR_MAP,
                         custom_data=['percent_of_budget', 'monthly_budget'],
                         hole=0.4)

    donut_chart.update_traces(
        hovertemplate='You have spent $%{value} on %{label} <br> That is %{customdata[0][0]:.1f}% of your budgeted $%{customdata[0][1]} and %{percent} of your total spending <extra></extra>',
        texttemplate='%{label}: $%{value}',  # what shows on the chart
        textposition='inside',      # can also be 'outside'
        textfont=dict(size=12),
    )

    donut_chart.update_layout(
        width=425,       # increase width (default ~450)
        height=450,      # increase height
        margin=dict(t=40, b=0, l=0, r=0),  # optional: adjust margins
        showlegend = False,
    )
    

    # Embed the chart
    donut_chart_html = donut_chart.to_html(full_html=False)

    daily_spending_by_category = get_daily_spending_by_category(month, year)
    daily_spending_by_category['date'] = pd.to_datetime({'year': year, 'month': month, 'day': daily_spending_by_category['day']})
    daily_spending_by_category = daily_spending_by_category.drop(columns=['day'])

    print(daily_spending_by_category)

    bar_chart = px.bar(
            daily_spending_by_category,
            x='date',
            y='total_spent',
            color='category',
            color_discrete_map=COLOR_MAP,
            labels={'date': 'Date', 'total_spent': 'Total Spent', 'category': 'Category'},
        )

    bar_chart.update_layout(
        xaxis=dict(tickformat='%b %d', dtick="D2", tickangle=45),  # format date ticks
        yaxis=dict(title='Amount ($)', tickformat='$,'),  # format y-axis as currency
        height=500,
        width=900,
    )

    bar_chart_html = bar_chart.to_html(full_html=False)

    return render_template("monthly_summary.html",
                               active_page="monthly_summary",
                               categories=CATEGORIES,
                               donut_chart_html=donut_chart_html,
                               bar_chart_html=bar_chart_html,
                               current_year=current_year,
                               selected_month=month,
                               selected_year=year,
                               months=MONTHS
                               )


@app.route("/annual-summary")
def annual_summary():
    now = datetime.now()
    year = int(request.args.get("year", now.year))
    current_year = now.year

    monthly_spending_by_category = get_monthly_spending_by_category(year)
    monthly_spending_by_category['month_cat'] = monthly_spending_by_category['month'].apply(lambda x: calendar.month_abbr[int(x)])

    bar_chart = px.bar(
        monthly_spending_by_category,
        x='month_cat',           # x-axis: month or date
        y='total_spent',     # y-axis: amount spent
        color='category',    # stack by category
        color_discrete_map=COLOR_MAP,
        title='Monthly Spending by Category (Stacked Area)',
        labels={'month': 'Month', 'total_spent': 'Total Spent', 'category': 'Category'}
    )

    bar_chart.update_layout(
        xaxis=dict(tickformat="%b %Y"),  # format month as Jan 2025, etc.
        yaxis_title='Spending ($)',
        legend_title_text='Category',
        height=500,
        width=800,
    )

    bar_chart_html = bar_chart.to_html(full_html=False)
    return render_template("annual_summary.html", active_page="annual_summary", year=year, current_year=current_year, bar_chart_html=bar_chart_html)

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
        combined_df["date"] = pd.to_datetime(combined_df["date"], errors='coerce')
        return render_template("review_transactions.html",
                               transactions=combined_df.to_dict(orient='records'),
                               categories=CATEGORIES,
                               sinking_funds=SINKING_FUNDS
                               )

    else:
        return render_template("confirmation_page.html", message="No valid CSV files uploaded.")


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
        sinking_fund_id = int(request.form.get(f"sinking_fund_{i}"))

        transaction_row = {
            "date": request.form.get(f"date_{i}"),
            "description": request.form.get(f"description_{i}"),
            "amount": float(request.form.get(f"amount_{i}")),
            "category_id": int(request.form.get(f"category_id_{i}")),
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

    print("All transaction rows:", all_transaction_rows)
    print("All sinking fund rows:", all_sinking_fund_rows)

    if save_transactions(pd.DataFrame(all_transaction_rows)) and save_sinking_fund_transactions(pd.DataFrame(all_sinking_fund_rows)):
        return render_template("confirmation_page.html", message="Transactions saved successfully!")
    return render_template("confirmation_page.html", message="Failed to save transactions.")


def get_reimbursement_amount(raw_reimbursement_amount):
    if raw_reimbursement_amount == "":
        return 0
    return raw_reimbursement_amount


def get_reimbursement_status(raw_reimbursement_status):
    if raw_reimbursement_status == "1":
        return True
    return False


def get_fund_id(fund_name):
    if fund_name in SINKING_FUNDS:
        return SINKING_FUNDS.get(fund_name).get("id")
    else:
        return None


def get_category_id(category):
    print(category)
    category_id = CATEGORIES.get(category).get("id")
    return category_id


@app.route("/manual-entry")
def manual_entry():
    return render_template("manual_entry.html", 
                           active_page="manual_entry", 
                           categories=CATEGORIES, 
                           payment_methods=PAYMENT_METHODS
                           )


@app.route("/manual-entry-spending", methods=["POST"])
def manual_entry_spending():
    num_entries = int(request.form.get("spending_num_entries", 0))
    row_list = []

    for i in range(num_entries):
        date = request.form.get(f"transaction_date[{i}]")
        description = request.form.get(f"description[{i}]")
        amount = request.form.get(f"amount[{i}]")
        category_id = int(request.form.get(f"category_id[{i}]"))
        payment_method = request.form.get(f"payment_method[{i}]")

        new_row = {
            "date": datetime.strptime(date, "%Y-%m-%d"),
            "description": description,
            "amount": float(amount) if amount else 0.0,
            "category_id": category_id,
            "payment_method": payment_method, 
            "reimbursed": False,
            "reimbursement_amount": 0,
        }

        row_list.append(new_row)

        df = pd.DataFrame(row_list)

    return render_template("review_transactions.html", 
                           transactions=df.to_dict(orient='records'), 
                           categories=CATEGORIES, 
                           sinking_funds=SINKING_FUNDS
                           )


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

@app.route("/default-sinking-contributions", methods=["POST"])
def default_sinking_contributions():
    print(request.form)
    sinking_fund_dict = get_fund_contributions()
    current_fund_values = get_sinking_fund_values()
    print("Current fund values:", current_fund_values)
    print(sinking_fund_dict)
    transaction_rows = []
    sinking_fund_transaction_rows = []
    for fund in sinking_fund_dict.keys():
        current_value = current_fund_values.get(fund).get("fund_value")
        print(f"Current value for fund {fund}:", current_value)
        default_contribution = sinking_fund_dict.get(fund).get("default_contribution")
        cap = sinking_fund_dict.get(fund).get("cap")
        print(f"The cap for {fund}: {cap}")
        category_id = sinking_fund_dict.get(fund).get("contribution_category_id")
        fund_id = sinking_fund_dict.get(fund).get("id")
        new_transaction_row = {
            "date": datetime.strptime(request.form.get("contribution_date"), "%Y-%m-%d"),
            "description": f"Sinking fund contribution for {fund}",
            "amount": default_contribution,
            "category_id": category_id,
            "payment_method": "Transfer",
            "reimbursed": False,
            "reimbursement_amount": 0,
        }
        transaction_rows.append(new_transaction_row)

        new_sinking_fund_transaction_row = {
            "fund_id": fund_id,
            "date": datetime.strptime(request.form.get("contribution_date"), "%Y-%m-%d"),
            "description": f"Sinking fund contribution for {fund}",
            "amount": default_contribution
        }

        if current_value >= cap:
            print(f"Current value for {fund} is already at or above the cap. No contribution made.")
        else:
            sinking_fund_transaction_rows.append(new_sinking_fund_transaction_row)

    transaction_df = pd.DataFrame(transaction_rows)
    sinking_fund_transaction_df = pd.DataFrame(sinking_fund_transaction_rows)
    if save_transactions(transaction_df) and save_sinking_fund_transactions(sinking_fund_transaction_df):
        return render_template("confirmation_page.html", message="Sinking fund transactions saved successfully")
    return render_template("confirmation_page.html", message="Failed to save sinking fund transactions")


@app.route("/settings")
def settings():
    return render_template("settings.html", active_page="settings")


@app.route("/delete-all-data")
def delete_all_data():
    result = delete_all_data_from_db()

    if result:
        return render_template("confirmation_page.html", message="All data has been successfully deleted.")
    return render_template("confirmation_page.html", message="Failed to delete all data.")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


