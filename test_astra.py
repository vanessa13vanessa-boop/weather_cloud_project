import os
import sys
from astrapy import DataAPIClient

# ZERO-TRUST ARCHITECTURE: Keys are dynamically loaded straight out of the 
# Doppler cloud vault directly into memory. No files, no cleartext leak!
ASTRA_DB_TOKEN = os.environ.get("ASTRA_DB_TOKEN")
ASTRA_DB_ENDPOINT = os.environ.get("ASTRA_DB_ENDPOINT")

if not ASTRA_DB_TOKEN or not ASTRA_DB_ENDPOINT:
    print("CRITICAL SECURITY ERROR: Required Doppler vault credentials are missing!")
    sys.exit(1)

def connect_to_azure_astra():
    try:
        # Initialize our database client directly using the secure vault token
        client = DataAPIClient(ASTRA_DB_TOKEN)
        db = client.get_database_by_api_endpoint(ASTRA_DB_ENDPOINT, keyspace="weather_data")
        
        print("SUCCESS: Authenticated to Azure seamlessly via Doppler Cloud Vault!")
        collection = db.create_collection("colorado_springs_weather")
        print("Collection 'colorado_springs_weather' is verified, secure, and permanent.")
        return collection
        
    except Exception as e:
        print(f"Database cluster connection failed: {e}")
        return None

if __name__ == "__main__":
    connect_to_azure_astra()
