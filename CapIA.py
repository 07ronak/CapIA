import csv
import re
import os
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

# Function to detect the delimiter
def detect_delimiter(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        sample = f.read(1024) ###
        sniffer = csv.Sniffer()  # CSV Sniffer detects the delimiter
        return sniffer.sniff(sample).delimiter

def normalize_column_name(column_name):
    return re.sub(r'[^a-zA-Z0-9]+', '_', column_name.strip().lower())

# Function to clean and standardize monetary values
def clean_amount(amount_str):
    if not amount_str or not re.search(r'\d', amount_str): # Check if the string contains digits
        return Decimal('0.00') # Return a default value if it's not a valid number
    try:
        negative = "-" if "-" in amount_str else ""  # Preserve negative signs if present ##
        amount_str = re.sub(r'[^\d.,]', '', amount_str)  # Remove all non-numeric and non-decimal characters except '-'
        amount_str = re.sub(r'(?<=\d)[.,](?=\d{3}(?:[.,]|$))', '', amount_str)  # Remove thousand separators
        amount_str = amount_str.replace(',', '.')   # Convert to a consistent decimal format
        return Decimal(f"{negative}{amount_str}") # Convert to a Decimal object
    except (InvalidOperation, ValueError):
        print(f"Warning: Invalid amount format '{amount_str}', defaulting to 0.00")
        return Decimal('0.00')

def normalize_status(status):
    return status.strip().lower()

# Function to standardize date formats
def normalize_date(date_str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()  # Convert to a date object
        except ValueError:
            continue # Try the next format if conversion fails
    raise ValueError(f"Unrecognized date format: {date_str}") ###


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
    } ###
    
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar='"') ###list()
        
        first_row = next(reader) ###reader[0]
        
        if has_headers(file_path):
            headers = [normalize_column_name(col) for col in first_row] ###reader = reader[1:] (dr)
        else:
            headers = list(expected_columns.keys()) ### headers = expected_columns (dr-)
            reader = csv.reader(open(file_path, 'r', newline='', encoding='utf-8'), delimiter=delimiter, quotechar='"')
            
        col_indices = {}  #empty dictionary
        # Matches column names with their positions in the CSV file.

        for i in range(len(headers)):
            column_name = headers[i]  # Get the column name at index i

            if column_name in expected_columns:  # Check if the column is in expected_columns
                col_indices[column_name] = i  # Add it to the dictionary with its index

        normalized_data = [] #empty list
        
        for row in reader: ##
            if len(row) != len(headers):
                print(f"Skipping row due to column mismatch: {row}")
                continue
            
            # Extract relevant columns
            data_dict = {}  #empty dictionary

            for key in col_indices:  
                column_index = col_indices[key]  # Get the corresponding index in row
                data_dict[key] = row[column_index]  # Extract value from row and store in dictionary
            
            if 'transaction_date' in data_dict:
                data_dict['transaction_date'] = normalize_date(data_dict['transaction_date'])
            if 'amount' in data_dict:
                data_dict['amount'] = clean_amount(data_dict['amount'])
            if 'status' in data_dict:
                data_dict['status'] = normalize_status(data_dict['status'])
            
            normalized_data.append(data_dict)
    
    return normalized_data #list of dict

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
