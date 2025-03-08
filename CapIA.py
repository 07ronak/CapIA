import csv
import re
import os
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

def detect_delimiter(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        sample = f.read(1024)
        sniffer = csv.Sniffer()
        return sniffer.sniff(sample).delimiter

def normalize_column_name(column_name):
    return re.sub(r'[^a-zA-Z0-9]+', '_', column_name.strip().lower())

def clean_amount(amount_str):
    if not amount_str or not re.search(r'\d', amount_str):
        return Decimal('0.00')
    try:
        negative = "-" if "-" in amount_str else ""
        amount_str = re.sub(r'[^\d.,]', '', amount_str)  # Remove all non-numeric and non-decimal characters except '-'
        amount_str = re.sub(r'(?<=\d)[.,](?=\d{3}(?:[.,]|$))', '', amount_str)  # Remove thousand separators
        amount_str = amount_str.replace(',', '.')
        return Decimal(f"{negative}{amount_str}")
    except (InvalidOperation, ValueError):
        print(f"Warning: Invalid amount format '{amount_str}', defaulting to 0.00")
        return Decimal('0.00')

def normalize_status(status):
    return status.strip().lower()

def normalize_date(date_str):
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
    delimiter = detect_delimiter(file_path)
    expected_columns = {
        'transaction_date': None,
        'description': None,
        'amount': None,
        'currency': None,
        'status': None
    }
    
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar='"')
        first_row = next(reader)
        
        if has_headers(file_path):
            headers = [normalize_column_name(col) for col in first_row]
        else:
            headers = list(expected_columns.keys())
            reader = csv.reader(open(file_path, 'r', newline='', encoding='utf-8'), delimiter=delimiter, quotechar='"')
            
        col_indices = {headers[i]: i for i in range(len(headers)) if headers[i] in expected_columns}
        
        normalized_data = []
        for row in reader:
            if len(row) != len(headers):
                print(f"Skipping row due to column mismatch: {row}")
                continue
            
            data_dict = {key: row[col_indices[key]] for key in col_indices}
            
            if 'transaction_date' in data_dict:
                data_dict['transaction_date'] = normalize_date(data_dict['transaction_date'])
            if 'amount' in data_dict:
                data_dict['amount'] = clean_amount(data_dict['amount'])
            if 'status' in data_dict:
                data_dict['status'] = normalize_status(data_dict['status'])
            
            normalized_data.append(data_dict)
    
    return normalized_data

def save_json(data, output_path):
    os.makedirs("JSON", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, default=str)

# Usage
file_path = "no_header.csv"
output_json_path = "JSON/no_header.json"

data = process_csv(file_path)
save_json(data, output_json_path)

for row in data:
    print(row)
