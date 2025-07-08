from google import genai
import json
import os
from dotenv import load_dotenv
print(os.environ.get("GEMINI_API_KEY"))

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))




def categorize_transactions(df):
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents= f"Please categorize the following descriptions in JSON format.\
    \
    The categories I want you to use are: Grocery, Dining, Shopping, Transportation, Housing, Entertainment, Travel, Other: \
    Here is a description of each category: \
    Grocery: Transactions from grocery stores, liquor stores or markets, for food and household items.\
    Dining: Meals or food from restaurants, fast food, cafes, or delivery services.\
    Shopping: Retail purchases from department stores, electronics shops, and online retailers.\
    Transportation: Purchases at gas stations, ridesharing services, or public transport fares.\
    Housing: Rent, mortgage, or home-related services.\
    Entertainment: Events, concerts, movie tickets, or subscriptions.\
    Travel: Flights, hotels, car rentals, or travel bookings.\
    Other: Miscellaneous purchases that don't fit in other categories.\
    Please use Other when you are unsure of the category.\
    \
    Use this JSON schema:\
    Categorized = {{'Description': 'Category'}}\
    This means that the JSON should be one single dictionary where each key is a discription in the given list and the value is the category you assign.\
    Example Structure to return: [{{'Uber': 'Transportation', 'Amazon': 'Shopping'}}]\
    Here is the list of descriptions: {df['Description'].tolist()}",
    config={
            'response_mime_type': 'application/json'
        },
    )
    print(response.text)

    category_map = json.loads(response.text)[0]

    df["Category"] = df["Description"].map(category_map)

    return df
