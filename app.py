from flask import Flask, render_template, request
from csv_cleaning import clean_apple, clean_amex

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_files = request.files.getlist("files")
    labels = request.form.getlist("labels")
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

            print(cleaned_data)
    
    return "Files uploaded successfully!"

if __name__ == "__main__":
    app.run(debug=True)