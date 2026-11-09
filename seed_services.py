from pymongo.errors import PyMongoError

from database import connect_to_database
from service_db import services


client = None

try:
    client, database = connect_to_database()
    service_collection = database["services"]

    service_collection.create_index("code", unique=True)

    for service in services:
        service_collection.update_one(
            {"code": service["code"]},
            {"$set": service},
            upsert=True
        )

        print(f'Saved: {service["name"]}')

    print()
    print("Services successfully saved to MongoDB Atlas!")
    print("Number of services:", service_collection.count_documents({}))

except (PyMongoError, RuntimeError) as error:
    print("Could not save services.")
    print(error)

finally:
    if client is not None:
        client.close()