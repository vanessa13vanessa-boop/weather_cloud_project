import os
import json
import io
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery
from google.oauth2 import service_account
from astrapy import DataAPIClient

ASTRA_TABLE = "woodland_park_weather"

def get_astra_client():
    astra_token = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
    astra_api_endpoint = os.environ["ASTRA_DB_API_ENDPOINT"]
    return DataAPIClient(astra_token).get_database_by_api_endpoint(
        astra_api_endpoint,
        keyspace="weather_data"
    )

def fetch_yesterdays_observations():
    db = get_astra_client()

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    yesterday_str = str(yesterday)

    collection = db.get_collection(ASTRA_TABLE)

    # Fetch ALL rows (safe fallback since Astra filters are limited)
    cursor = collection.find({})
    all_rows = list(cursor)

    # Filter by timestamp prefix in Python
    rows = [
        r for r in all_rows
        if r.get("timestamp", "").startswith(yesterday_str)
    ]

    return rows, yesterday_str

def compute_daily_summary(rows, date_str):
    if not rows:
        return None

    temps = [r.get("temperature_f") for r in rows if r.get("temperature_f") is not None]
    rainfall = [r.get("precip_mm") for r in rows if r.get("precip_mm") is not None]
    summaries = [r.get("summary") for r in rows if r.get("summary")]

    return {
        "date": date_str,
        "source_run_time": datetime.now(timezone.utc).isoformat(),
        "high_actual_f": max(temps) if temps else None,
        "low_actual_f": min(temps) if temps else None,
        "rain_actual_mm": sum(rainfall) if rainfall else 0,
        "summary_actual": summaries[-1] if summaries else None
    }

def write_to_bigquery(row):
    creds_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)

    client = bigquery.Client(
        project=os.environ["BQ_PROJECT_ID"],
        credentials=credentials
    )

    table_id = os.environ["BQ_OBSERVED_TABLE"]

    ndjson_data = json.dumps(row) + "\n"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=False,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    load_job = client.load_table_from_file(
        io.BytesIO(ndjson_data.encode("utf-8")),
        table_id,
        job_config=job_config
    )

    load_job.result()
    print("Loaded 1 observed summary row into BigQuery.")

if __name__ == "__main__":
    rows, date_str = fetch_yesterdays_observations()
    print(f"Fetched {len(rows)} rows for {date_str}")

    summary = compute_daily_summary(rows, date_str)
    print("Daily summary:", summary)

    if summary:
        write_to_bigquery(summary)
        print("Observation summary load completed.")
    else:
        print("No observations found for yesterday — nothing loaded.")

