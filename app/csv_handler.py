import csv
import os

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
        f'Current Price ({currency_choice})': price,
        '1h%': volume_1h,
        '24h%': volume_24h,
        '7d%': volume_7d,
        f'Market Cap ({currency_choice})': market_cap,
        'Logo': logo,
        'Symbol': symbol,
        'Description': description,
        'Creation Date': date_added,
        'Website': website,
        'Source Code': source_code
    })
    print(result)
    return result