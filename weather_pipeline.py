import os
import sys
import requests
from datetime import datetime, timezone
from astrapy import DataAPIClient

# 1. Zero-Trust Verification: Fetch secrets directly from Doppler runtime memory
ASTRA_DB_TOKEN = os.environ.get("ASTRA_DB_TOKEN")
ASTRA_DB_ENDPOINT = os.environ.get("ASTRA_DB_ENDPOINT")

if not ASTRA_DB_TOKEN or not ASTRA_DB_ENDPOINT:
    print("CRITICAL SECURITY ERROR: Pipeline credentials missing from runtime memory!")
    sys.exit(1)

# 2. Pipeline Configurations
TARGET_URL = "https://api.weather.gov/stations/KCOS/observations/latest"
HEADERS = {
    "User-Agent": "(CloudWeatherPipelineResumeProject, tracking_weather@example.com)"
}

def fetch_and_stream_weather():
    try:
        # A. Extract data from the REST API
        print(f"Extracting live data from National Weather Service API ({TARGET_URL})...")
        response = requests.get(TARGET_URL, headers=HEADERS)
        response.raise_for_status()

        raw_data = response.json()
        props = raw_data['properties']

        # B. Transform JSON payload into clean, structured records
        weather_record = {
            "timestamp": props.get("timestamp"), # ISO time-series format
            "station_id": "KCOS",
            "city": "Colorado Springs",
            "temperature_c": props['temperature'].get('value') if props.get('temperature') else None,
            "relative_humidity": props['relativeHumidity'].get('value') if props.get('relativeHumidity') else None,
            "wind_speed_kmh": props['windSpeed'].get('value') if props.get('windSpeed') else None,
            "summary": props.get("textDescription"), # e.g., "Clear" or "Mostly Cloudy"
            "ingested_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        # C. Connect and stream data to Astra NoSQL collection
        client = DataAPIClient(ASTRA_DB_TOKEN)
        db = client.get_database_by_api_endpoint(ASTRA_DB_ENDPOINT, keyspace="weather_data")
        collection = db.get_collection("colorado_springs_weather")

        print(f"Streaming live observations to Astra NoSQL...")
        insert_result = collection.insert_one(weather_record)

        print(f"🚀 SUCCESS! Record pushed with cloud document ID: {insert_result.inserted_id}")
        print(f"Details: {weather_record['summary']} | Temp: {weather_record['temperature_c']}C")

    except Exception as e:
        print(f"❌ Pipeline Execution Failed: {e}")

if __name__ == "__main__":
    fetch_and_stream_weather()
