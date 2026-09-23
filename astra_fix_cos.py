from astrapy import DataAPIClient
import os

client = DataAPIClient(os.environ["ASTRA_DB_APPLICATION_TOKEN"])
db = client.get_database_by_api_endpoint(
    os.environ["ASTRA_DB_API_ENDPOINT"],
    keyspace=os.environ["ASTRA_DB_KEYSPACE"]
)

try:
    db.delete_collection("colorado_springs_weather")
    print("Deleted corrupted collection.")
except Exception as e:
    print("Collection may not exist yet:", e)

db.create_collection("colorado_springs_weather")
print("Recreated colorado_springs_weather collection cleanly.")
