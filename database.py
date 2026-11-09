import os
import certifi

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()


def connect_to_database():
    connection_string = os.getenv("MONGODB_URI")

    if not connection_string:
        raise RuntimeError(
            "MONGODB_URI is missing. Create a .env file with the Atlas connection string."
        )

    client = MongoClient(
        connection_string,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=5000,
        tlsCAFile=certifi.where()
    )

    client.admin.command("ping")
    database = client["cleanride"]

    return client, database