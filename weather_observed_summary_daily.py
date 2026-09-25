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

def fetch_metar_rows(client, date_str):
    query = f"""
        SELECT *
        FROM `{os.environ['BQ_OBSERVED_METAR_TABLE']}`
        WHERE DATE(TIMESTAMP(timestamp)) = '{date_str}'
    """
    return list(client.query(query))

def compute_daily_summary(rows):
    temps_f = []
    summaries = []

    for r in rows:
        if r["temp"] is not None:
            temps_f.append(r["temp"] * 9/5 + 32)

        if r["text_description"]:
            summaries.append(r["text_description"])

    return {
        "high_actual_f": max(temps_f) if temps_f else None,
        "low_actual_f": min(temps_f) if temps_f else None,
        "rain_actual_mm": None,  # METAR doesn't include rain in your current schema
        "summary_actual": max(set(summaries), key=summaries.count) if summaries else None
    }

def write_daily_summary(summary, date_str):
    client = get_bigquery_client()
    table_id = os.environ["BQ_OBSERVED_TABLE"]

    row = {
        "date": date_str,
        "source_run_time": datetime.now(timezone.utc).isoformat(),
        **summary
    }

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
    print("Loaded daily observed summary into BigQuery.")

if __name__ == "__main__":
    client = get_bigquery_client()

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    date_str = str(yesterday)

    rows = fetch_metar_rows(client, date_str)

    if not rows:
        print("No METAR rows found — cannot compute daily summary.")
        exit(0)

    summary = compute_daily_summary(rows)
    write_daily_summary(summary, date_str)
    print("Daily observed summary completed.")
