import csv
import re
import os
import json
from datetime import datetime
from decimal import Decimal

def detect_delimiter(file_path):
    # Detects the delimiter used in the CSV file. 
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        sample = f.read(1024)  # Read a small portion of the file
        sniffer = csv.Sniffer()
        return sniffer.sniff(sample).delimiter
    
def normalize_column_name(column_name):
    #Converts column names to snake_case.
    return re.sub(r'[\s\-]+', '_', column_name.strip().lower())

def clean_amount(amount_str):
    #Converts an amount string to Decimal after removing thousand separators.
    if amount_str:
        # Handle both comma and dot as decimal separators
        amount_str = amount_str.replace(",", "") if "." in amount_str else amount_str.replace(".", "").replace(",", ".")
        return Decimal(amount_str)
    return Decimal('0.00')

def normalize_status(status):
    return status.strip().lower()

def normalize_date(date_str):
    #Converts various date formats to YYYY-MM-DD.
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {date_str}")

def has_headers(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        sample = f.read(1024)
        return csv.Sniffer().has_header(sample)

def process_csv(file_path):
    #Reads and normalizes the CSV file
    delimiter = detect_delimiter(file_path)
    column_mapping = {
        0: 'transaction_date',
        1: 'description',
        2: 'amount',
        3: 'currency',
        4: 'status'
    }

    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar='"')
        headers = next(reader)

        if has_headers(file_path):
            headers = [normalize_column_name(col) for col in headers]
        else:
            headers = [column_mapping[i] for i in range(len(column_mapping))]

        normalized_data = []
        for row in reader:
            if len(row) != len(headers):
                print(f"Skipping row due to column mismatch: {row}")
                continue  # Skip invalid rows

            data_dict = dict(zip(headers, row))

            # Apply transformations
            data_dict['transaction_date'] = normalize_date(data_dict.get('transaction_date', ''))
            data_dict['amount'] = clean_amount(data_dict.get('amount', ''))
            data_dict['status'] = normalize_status(data_dict.get('status', ''))
            
            normalized_data.append(data_dict)

    return normalized_data

def save_json(data, output_path):
    os.makedirs("JSON", exist_ok=True)  # Ensure the "JSON" directory exists
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, default=str)  # Save data as formatted JSON


# Usage
file_path = "test3.csv"
output_json_path = "JSON/output.json"

data = process_csv(file_path)
save_json(data, output_json_path)

for row in data:
    print(row)
