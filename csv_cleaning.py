import pandas as pd
from gemeni_sorting import categorize_transactions


def clean_apple(csv_file):
    df = pd.read_csv(csv_file)
    if not df.empty:
        df = df[(~df["Description"].str.contains("ACH DEPOSIT INTERNET TRANSFER", case=False))]
        df = categorize_transactions(df)
        df = df[["Transaction Date", "Description", "Category", "Amount (USD)"]]
        df = df.rename(columns={"Transaction Date": "date", "Amount (USD)": "amount", "Description": "description", "Category": "category"})

        return df

def clean_amex(csv_file):
    df = pd.read_csv(csv_file)
    if not df.empty:
        print(df)
        df = df[(~df["Description"].str.contains("AUTOPAY PAYMENT", case=False))]
        df = categorize_transactions(df)
        df = df[["Date", "Description", "Amount", "Category"]]
        df = df.rename(columns={"Date": "date", "Amount": "amount", "Description": "description", "Category": "category"})

        return df