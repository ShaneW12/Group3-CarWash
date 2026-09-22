from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    client = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    database = client["cleanride"]

    print("Successfully connected to MongoDB!")
    print("Database selected:", database.name)

except ConnectionFailure as error:
    print("Could not connect to MongoDB.")
    print(error)

finally:
    if "client" in locals():
        client.close()