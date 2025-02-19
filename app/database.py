# app/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings  # Import settings from config.py

# Create an instance of AsyncIOMotorClient using the configured MongoDB URI.
client = AsyncIOMotorClient(settings.mongo_uri)
db_name = settings.mongo_db_name  # Get the database name from settings.

# Set up the database instance.
db = client.get_database(db_name)


async def test_connection():
    """
    Test the connection to MongoDB by listing the collections.
    """
    try:
        collections = await db.list_collection_names()
        print("Connected to MongoDB. Collections available:", collections)
    except Exception as e:
        print("Error connecting to MongoDB:", e)
