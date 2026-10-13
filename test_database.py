from pymongo.errors import PyMongoError

from database import connect_to_database


client = None

try:
    client, database = connect_to_database()

    print("Successfully connected to MongoDB Atlas!")
    print("Database selected:", database.name)

except (PyMongoError, RuntimeError) as error:
    print("Could not connect to MongoDB Atlas.")
    print(error)

finally:
    if client is not None:
        client.close()