import os
import json
import io
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery
from google.oauth2 import service_account

def get_bigquery_client():
    creds_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)

    return bigquery.Client(
        project=os.environ["BQ_PROJECT_ID"],
        credentials=credentials
    )

def fetch_forecast_row(client, date_str):
    query = f"""
        SELECT *
        FROM `{os.environ['BQ_FORECAST_TABLE']}`
        WHERE date = '{date_str}'
        LIMIT 1
    """
    rows = list(client.query(query))
    return rows[0] if rows else None

def fetch_observed_row(client, date_str):
    query = f"""
        SELECT *
        FROM `{os.environ['BQ_OBSERVED_TABLE']}`
        WHERE date = '{date_str}'
        LIMIT 1
    """
    rows = list(client.query(query))
    return rows[0] if rows else None

def compute_accuracy(f, o, date_str):
    return {
        "date": date_str,
        "source_run_time": datetime.now(timezone.utc).isoformat(),
        "high_error_f": (o["high_actual_f"] - f["high_predicted_f"]) if o["high_actual_f"] is not None else None,
        "low_error_f": (o["low_actual_f"] - f["low_predicted_f"]) if o["low_actual_f"] is not None else None,
        "rain_error_mm": (o["rain_actual_mm"] - f["pop_predicted"]) if o["rain_actual_mm"] is not None else None,
        "summary_match_score": 1.0 if f["summary_predicted"] == o["summary_actual"] else 0.0
    }

def write_to_bigquery(row):
    client = get_bigquery_client()
    table_id = os.environ["BQ_ACCURACY_TABLE"]

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
    print("Loaded 1 accuracy row into BigQuery.")

if __name__ == "__main__":
    client = get_bigquery_client()

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    date_str = str(yesterday)

    print(f"Computing accuracy for {date_str}")

    forecast = fetch_forecast_row(client, date_str)
    observed = fetch_observed_row(client, date_str)

    if not forecast:
        print("No forecast row found — cannot compute accuracy.")
        exit(0)

    if not observed:
        print("No observed row found — cannot compute accuracy.")
        exit(0)

    accuracy_row = compute_accuracy(forecast, observed, date_str)
    print("Accuracy row:", accuracy_row)

    write_to_bigquery(accuracy_row)
    print("Accuracy computation completed.")
