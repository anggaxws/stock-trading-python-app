# stock-trading-python-app

This is an easy implementation for downloading stock ticker reference data from the Massive/Polygon API with Python.

The script is intentionally simple:
- it loads your API key from `.env`
- it requests ticker data page by page
- it stops after 5,000 records to stay within a small free-plan request budget
- it saves the extracted data as both JSON and CSV

## Run

Set your API key in `.env`:

```env
POLYGON_API_KEY=your_api_key_here
```

### Optional: Snowflake ingestion

Add Snowflake connection settings to `.env`:

```env
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_WAREHOUSE=your_snowflake_warehouse
SNOWFLAKE_DATABASE=your_snowflake_database
SNOWFLAKE_SCHEMA=your_snowflake_schema
SNOWFLAKE_ROLE=your_snowflake_role
```

### Install dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Because `snowflake-connector-python` includes a native extension, on Windows you may also need Build Tools:

- https://visualstudio.microsoft.com/visual-cpp-build-tools/

Or use Python 3.11/3.12 to get prebuilt wheels.

### Run data fetch and load

```bash
python script.py
```

### Optional scheduler

Run the scheduler script to execute every minute (for testing):

```bash
python scheduler.py
```

## Output

After running the script, you will get:
- `tickers.json` for the raw API data
- `TICKERS_RAW` table in Snowflake containing JSON variant rows (if Snowflake is configured)

This project is meant to be beginner-friendly and easy to extend later.
