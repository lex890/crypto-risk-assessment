import os
import csv
import pandas as pd
from decimal import Decimal
from forex_python.converter import CurrencyRates


def read_csv(filepath):
    # reinitialize (headings, data) if update happens in the csv
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

    if not data:
        return [], []
    headings = data[0]
    data = data[1:]
    return headings, data

def export_to_csv(list_of_dict, filepath='app/assets/data/temp.csv'):
    if not list_of_dict:
        print("No data to export.")
        return filepath
    if isinstance(list_of_dict, list) and all(isinstance(item, dict) for item in list_of_dict):
        # Extract fieldnames from keys of the first dictionary (act as a header)
        fieldnames = list_of_dict[0].keys()
        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(list_of_dict)
        print(f"✅ Data exported to {filepath}")
    if isinstance(list_of_dict, list) and all(isinstance(item, tuple) for item in list_of_dict):
        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(list_of_dict)
        print(f"✅ Data exported to {filepath}")
    else:
        print("Invalid data format. Expected a list of dictionaries or tuples.")
        return None

def append_csv(filepath, new_data):
    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in new_data:
            writer.writerow(row)
    os.remove('app/assets/data/temp.csv') 
    print(f"✅ New data appended to {filepath}")

def convert_to_dict(data, currency_choice):
    result = []
    for row in data:
        (
            ranking, name, price, volume_1h, volume_24h, volume_7d, market_cap,
            logo, symbol, description, date_added, website, source_code
        ) = row
    
    result.append({
        '#': ranking,
        'Name': name,
        f'Current Price': price,
        '1h%': volume_1h,
        '24h%': volume_24h,
        '7d%': volume_7d,
        'Market Cap': market_cap,
        'Logo': logo,
        'Symbol': symbol,
        'Description': description,
        'Creation Date': date_added,
        'Website': website,
        'Source Code': source_code
    })
    print(result)
    return result


def currency_conversion(current_csv, currency_choice, new_currency_choice):
    if currency_choice == new_currency_choice:
      return currency_choice
    df = pd.read_csv(current_csv)
    
    # Read the original column
    column_name_price = "Current Price"
    column_name_mcap = "Market Cap"
    if column_name_price not in df.columns:
        raise ValueError(f"Column '{column_name_price}' not found in CSV.")

    column_values_price = df[column_name_price].tolist()
    column_values_mcap = df[column_name_mcap].tolist()
    # Convert each value and collect results
    c = CurrencyRates()
    new_currency_result_price = []
    new_currency_result_mcap = []
    for value in column_values_price:
        try:
            numeric_value = Decimal(str(value).replace(",", "").strip())
            converted_value = round(c.convert(currency_choice, new_currency_choice, numeric_value), 2)
            formatted_value = f"{converted_value:,.2f}"  # Add commas and fix to 2 decimal places
            new_currency_result_price.append(formatted_value)
            print(f'new value {formatted_value}')
        except Exception as e:
            print(f"Error converting {value}: {e}")
            new_currency_result_price.append(None)  # Or handle however you want
    
    for value in column_values_mcap:
        try:
            numeric_value = Decimal(str(value).replace(",", "").strip())
            converted_value = round(c.convert(currency_choice, new_currency_choice, numeric_value), 2)
            formatted_value = f"{converted_value:,.2f}"  # Add commas and fix to 2 decimal places
            new_currency_result_mcap.append(formatted_value)
            print(f'new value {formatted_value}')
        except:
            print(f"Error converting {value}: {e}")
            new_currency_result_mcap.append(None)  # Or handle however you want
    # Replace old column with new values
    df[column_name_price] = new_currency_result_price
    df[column_name_mcap] = new_currency_result_mcap
    # Save the updated DataFrame
    df.to_csv(current_csv, index=False)

    print(f"✅ Conversion complete. Saved to: {current_csv}")
    return new_currency_choice

