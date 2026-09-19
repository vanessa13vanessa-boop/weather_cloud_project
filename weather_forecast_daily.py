import os
import json
import requests
import io
from datetime import datetime, timezone
from google.cloud import bigquery
from google.oauth2 import service_account

HEADERS = {
    "User-Agent": "(CloudWeatherPipelineForecast, tracking_weather@example.com)"
}

FORECAST_URL = "https://api.weather.gov/gridpoints/PUB/82,99/forecast"

def fetch_daily_forecast():
    resp = requests.get(FORECAST_URL, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()

    periods = data["properties"]["periods"]

    today = periods[0]
    tonight = periods[1]

    today_date = datetime.fromisoformat(today["startTime"]).date()

    return {
        "date": str(today_date),
        "source_run_time": datetime.now(timezone.utc).isoformat(),
        "high_predicted_f": today.get("temperature"),
        "low_predicted_f": tonight.get("temperature"),
        "pop_predicted": today.get("probabilityOfPrecipitation", {}).get("value"),
        "summary_predicted": today.get("shortForecast")
    }

def write_to_bigquery(row):
    # Load service account JSON from Doppler
    creds_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)

    client = bigquery.Client(
        project=os.environ["BQ_PROJECT_ID"],
        credentials=credentials
    )

    table_id = os.environ["BQ_FORECAST_TABLE"]

    # Convert row to NDJSON format (one JSON object per line)
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

    load_job.result()  # Wait for job to finish
    print("Loaded 1 row into BigQuery via batch load.")

if __name__ == "__main__":
    row = fetch_daily_forecast()
    print("Row to load:", row)
    write_to_bigquery(row)
    print("Load job completed.")
