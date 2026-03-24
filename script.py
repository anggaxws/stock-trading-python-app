import requests
import os
import json
import csv
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("POLYGON_API_KEY")

limit = 1000
max_records = 5000
json_output_path = "tickers.json"
csv_output_path = "tickers.csv"

url =f'https://api.massive.com/v3/reference/tickers?market=stocks&active=true&order=asc&limit={limit}&sort=ticker&apiKey={API_KEY}'
tickers = []
response = requests.get(url)
data = response.json()

if 'results' in data:
    remaining = max_records - len(tickers)
    tickers.extend(data['results'][:remaining])
else:
    print("Initial request failed:", data)
    exit()

while 'next_url' in data and len(tickers) < max_records:
    response = requests.get(data['next_url'] + f'&apiKey={API_KEY}')
    data = response.json()

    if 'results' not in data:
        print("Pagination failed:", data)
        break

    remaining = max_records - len(tickers)
    tickers.extend(data['results'][:remaining])

with open(json_output_path, "w", encoding="utf-8") as json_file:
    json.dump(tickers, json_file, indent=2)

fieldnames = sorted({key for ticker in tickers for key in ticker.keys()})

with open(csv_output_path, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for ticker in tickers:
        row = {}
        for field in fieldnames:
            value = ticker.get(field, "")
            if isinstance(value, (dict, list)):
                row[field] = json.dumps(value)
            else:
                row[field] = value
        writer.writerow(row)

print(len(tickers))
print(f"Saved JSON to {json_output_path}")
print(f"Saved CSV to {csv_output_path}")
