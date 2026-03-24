import requests
import os
import json
from dotenv import load_dotenv

# Load local .env values (this will also pick up POLYGON_API_KEY etc.)
load_dotenv()

API_KEY = os.getenv("POLYGON_API_KEY")

# Snowflake credentials loaded from environment via .env (do not hardcode secrets in source)
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")

if not all([SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_ROLE]):
    raise EnvironmentError("Snowflake credentials not fully set in environment. Please set SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_ROLE in .env")

limit = 1000
max_records = 5000
json_output_path = "tickers.json"

url = f"https://api.massive.com/v3/reference/tickers?market=stocks&active=true&order=asc&limit={limit}&sort=ticker&apiKey={API_KEY}"

tickers = []
response = requests.get(url)
data = response.json()

if "results" in data:
    remaining = max_records - len(tickers)
    tickers.extend(data["results"][:remaining])
else:
    print("Initial request failed:", data)
    raise SystemExit(1)

while "next_url" in data and len(tickers) < max_records:
    response = requests.get(data["next_url"] + f"&apiKey={API_KEY}")
    data = response.json()

    if "results" not in data:
        print("Pagination failed:", data)
        break

    remaining = max_records - len(tickers)
    tickers.extend(data["results"][:remaining])

# Save JSON for local debugging / archival
with open(json_output_path, "w", encoding="utf-8") as json_file:
    json.dump(tickers, json_file, indent=2)

print(f"Downloaded {len(tickers)} tickers.")

# Insert into Snowflake table
try:
    import snowflake.connector
except ImportError as e:
    raise ImportError("snowflake-connector-python is required: pip install snowflake-connector-python") from e

conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA,
    role=SNOWFLAKE_ROLE,
)

create_table_sql = """
CREATE TABLE IF NOT EXISTS TICKERS_RAW (
    LOAD_TS TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    TICKER_OBJECT VARIANT
)
"""

with conn.cursor() as cur:
    cur.execute(create_table_sql)

    insert_sql = "INSERT INTO TICKERS_RAW (TICKER_OBJECT) VALUES (PARSE_JSON(%s))"
    rows = [(json.dumps(t),) for t in tickers]

    # Batch insert in chunks
    chunk_size = 1000
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i : i + chunk_size]
        cur.executemany(insert_sql, chunk)

    conn.commit()

print(f"Inserted {len(tickers)} rows into Snowflake TICKERS_RAW.")

conn.close()
