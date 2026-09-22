from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    client = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    database = client["cleanride"]
    service_collection = database["services"]

    print("Services retrieved from MongoDB:")
    print("--------------------------------")

    for service in service_collection.find({}, {"_id": 0}).sort("name", 1):
        dollars = service["price_cents"] / 100
        print(f'{service["name"]}: ${dollars:.2f}')

except ConnectionFailure as error:
    print("Could not connect to MongoDB.")
    print(error)

finally:
    if "client" in locals():
        client.close()