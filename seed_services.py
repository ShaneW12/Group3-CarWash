from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from service import services


try:
    # Connect to the MongoDB server running on this computer
    client = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=5000
    )

    # Check that MongoDB is responding
    client.admin.command("ping")

    # Select the database and collection
    database = client["cleanride"]
    service_collection = database["services"]

    # Prevent two services from using the same code
    service_collection.create_index("code", unique=True)

    # Add or update every service
    for service in services:
        service_collection.update_one(
            {"code": service["code"]},
            {"$set": service},
            upsert=True
        )

        print(f'Saved: {service["name"]}')

    print()
    print("Services successfully saved to MongoDB!")
    print("Number of services:", service_collection.count_documents({}))

except ConnectionFailure as error:
    print("Could not connect to MongoDB.")
    print(error)

finally:
    if "client" in locals():
        client.close()