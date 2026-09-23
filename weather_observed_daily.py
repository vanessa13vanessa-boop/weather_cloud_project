import os
import requests
from datetime import datetime
from astrapy import DataAPIClient
from google.cloud import bigquery

# KCOS METAR JSON endpoint
METAR_URL = "https://api.weather.gov/stations/KCOS/observations/latest"

def fetch_metar():
    resp = requests.get(METAR_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    props = data["properties"]

    return {
        "timestamp": props["timestamp"],
        "temp": props["temperature"]["value"],
        "wind_speed": props["windSpeed"]["value"],
        "humidity": props["relativeHumidity"]["value"],
        "dewpoint": props["dewpoint"]["value"],
        "visibility": props["visibility"]["value"],
        "text_description": props["textDescription"],
    }

def insert_astra(doc):
    client = DataAPIClient(os.environ["ASTRA_DB_APPLICATION_TOKEN"])
    db = client.get_database_by_api_endpoint(
        os.environ["ASTRA_DB_API_ENDPOINT"],
        keyspace=os.environ["ASTRA_DB_KEYSPACE"]
    )
    collection = db.get_collection(os.environ["ASTRA_DB_COLLECTION"])

    # Avoid duplicates
    existing = list(collection.find({"timestamp": doc["timestamp"]}))
    if existing:
        print("Already inserted:", doc["timestamp"])
        return

    collection.insert_one(doc)
    print("Inserted into Astra:", doc["timestamp"])

def insert_bigquery(doc):
    import json
    import io
    from google.oauth2 import service_account

    creds_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)

    client = bigquery.Client(
        project=os.environ["BQ_PROJECT_ID"],
        credentials=credentials
    )

    table_id = os.environ["BQ_OBSERVED_TABLE"]

    ndjson_data = json.dumps({
        "timestamp": doc["timestamp"],
        "temp": doc["temp"],
        "wind_speed": doc["wind_speed"],
        "humidity": doc["humidity"],
        "dewpoint": doc["dewpoint"],
        "visibility": doc["visibility"],
        "text_description": doc["text_description"],
        "source_run_time": datetime.utcnow().isoformat()
    }) + "\n"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        autodetect=False,
    )

    load_job = client.load_table_from_file(
        io.BytesIO(ndjson_data.encode("utf-8")),
        table_id,
        job_config=job_config
    )

    load_job.result()
    print("Inserted into BigQuery:", doc["timestamp"])


def main():
    doc = fetch_metar()
    insert_astra(doc)
    insert_bigquery(doc)

if __name__ == "__main__":
    main()