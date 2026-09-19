import os
import sys
import requests
from datetime import datetime, timezone
from astrapy import DataAPIClient

# -----------------------------
# 1. Zero-Trust Secret Loading
# -----------------------------
ASTRA_DB_TOKEN = os.environ.get("ASTRA_DB_TOKEN")
ASTRA_DB_ENDPOINT = os.environ.get("ASTRA_DB_ENDPOINT")

if not ASTRA_DB_TOKEN or not ASTRA_DB_ENDPOINT:
    print("CRITICAL SECURITY ERROR: Pipeline credentials missing from runtime memory!")
    sys.exit(1)

HEADERS = {
    "User-Agent": "(CloudWeatherPipelineResumeProject, tracking_weather@example.com)"
}

# -----------------------------
# 2. Conversion Helpers
# -----------------------------
def celsius_to_fahrenheit(celsius_val):
    if celsius_val is None:
        return None
    return round((celsius_val * 9/5) + 32, 1)

def kmh_to_mph(kmh_val):
    if kmh_val is None:
        return None
    return round(kmh_val * 0.621371, 1)

# -----------------------------
# 3. Resolve Nearest NWS Station
# -----------------------------
def get_nearest_station(lat, lon):
    try:
        print(f"Resolving nearest NWS station for lat={lat}, lon={lon}...")

        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        points_resp = requests.get(points_url, headers=HEADERS)
        points_resp.raise_for_status()

        stations_url = points_resp.json()["properties"]["observationStations"]

        stations_resp = requests.get(stations_url, headers=HEADERS)
        stations_resp.raise_for_status()

        stations = stations_resp.json()["observationStations"]
        nearest_station = stations[0].split("/")[-1]

        print(f"Nearest station resolved: {nearest_station}")
        return nearest_station

    except Exception as e:
        print(f"❌ Failed to resolve nearest station: {e}")
        sys.exit(1)

# -----------------------------
# 4. Fetch Latest Observation
# -----------------------------
def fetch_latest_observation(station_id):
    try:
        url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
        print(f"Fetching latest observation from {url}...")

        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()

        return resp.json()

    except Exception as e:
        print(f"❌ Failed to fetch latest observation: {e}")
        sys.exit(1)

# -----------------------------
# 5. Transform → Woodland Park Record
# -----------------------------
def transform_weather_record(raw):
    props = raw.get("properties", {})

    temp_c = props.get("temperature", {}).get("value")
    wind_kmh = props.get("windSpeed", {}).get("value")

    return {
        "timestamp": props.get("timestamp"),
        "station_id": raw.get("id", "").split("/")[-1],
        "city": "Woodland Park",
        "temperature_celsius": temp_c,
        "temperature_fahrenheit": celsius_to_fahrenheit(temp_c),
        "relative_humidity": props.get("relativeHumidity", {}).get("value"),
        "wind_speed_kmh": wind_kmh,
        "wind_speed_mph": kmh_to_mph(wind_kmh),
        "summary": props.get("textDescription"),
        "ingested_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

# -----------------------------
# 6. Stream to Astra NoSQL
# -----------------------------
def stream_to_astra(record):
    try:
        client = DataAPIClient(ASTRA_DB_TOKEN)
        db = client.get_database_by_api_endpoint(ASTRA_DB_ENDPOINT, keyspace="weather_data")

                # Safe existence check
        existing = db.list_collections()

        if "woodland_park_weather" in existing:
            collection = db.get_collection("woodland_park_weather")
        else:
            print("Creating new collection 'woodland_park_weather'...")
            collection = db.create_collection("woodland_park_weather")

        print("Streaming record to Astra NoSQL...")
        result = collection.insert_one(record)

        print(f"🚀 SUCCESS! Record ID: {result.inserted_id}")
        print(f"Metrics: {record['city']} | {record['temperature_fahrenheit']}°F | {record['summary']}")

    except Exception as e:
        print(f"❌ Astra streaming failed: {e}")
        sys.exit(1)


# -----------------------------
# 7. Main Pipeline
# -----------------------------
def run_pipeline():
    lat = 38.9939
    lon = -105.0569

    station_id = get_nearest_station(lat, lon)
    raw_obs = fetch_latest_observation(station_id)
    record = transform_weather_record(raw_obs)
    stream_to_astra(record)

if __name__ == "__main__":
    run_pipeline()
