import csv

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

def export_to_csv(list_of_dict, filepath='./data/temp.csv'):
    if not list_of_dict:
        print("No data to export.")
        return filepath
    # Extract fieldnames from keys of the first dictionary (act as a header)
    fieldnames = list_of_dict[0].keys()
    with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(list_of_dict)

    print(f"✅ Data exported to {filepath}")

def append_csv(filepath, new_data):
    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in new_data:
            writer.writerow(row)
    print(f"✅ New data appended to {filepath}")