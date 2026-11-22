from pymongo.errors import PyMongoError
from database import connect_to_database

client = None

try:
    client, database = connect_to_database()
    service_collection = database["services"]

    print("Services retrieved from MongoDB Atlas:")
    print("---------------------------------------")

    services = service_collection.find({}, {"_id": 0}).sort("name", 1)

    for service in services:
        dollars = service["price_cents"] / 100
        print(f'{service["name"]}: ${dollars:.2f}')

    print("---------------------------------------")
    print(
        "Number of services:",
        service_collection.count_documents({})
    )

except (PyMongoError, RuntimeError) as error:
    print("Could not retrieve services.")
    print(error)

finally:
    if client is not None:
        client.close()