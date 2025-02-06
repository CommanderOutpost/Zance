import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from bson.objectid import ObjectId

# Connect to MongoDB
client = AsyncIOMotorClient(settings.mongo_uri)
db = client.get_default_database()
ai_collection = db.ais

# Dummy AI agents
dummy_ais = [
    {
        "name": "FriendlyBot",
        "age": 3,
        "details": "A friendly and helpful AI assistant that loves to chat.",
        "personality": "friendly",
    },
    {
        "name": "TechGuru",
        "age": 5,
        "details": "A highly knowledgeable AI specialized in technology and software development.",
        "personality": "technical",
    },
    {
        "name": "JokerBot",
        "age": 2,
        "details": "A humorous AI that cracks jokes and lightens up conversations.",
        "personality": "funny",
    },
    {
        "name": "StoicAI",
        "age": 7,
        "details": "A wise AI that provides deep philosophical insights and Stoic wisdom.",
        "personality": "philosophical",
    },
    {
        "name": "CryptoMaster",
        "age": 4,
        "details": "An AI expert in cryptocurrencies, blockchain, and trading.",
        "personality": "financial",
    },
    {
        "name": "HealthBuddy",
        "age": 3,
        "details": "A virtual health assistant that gives advice on fitness, nutrition, and well-being.",
        "personality": "caring",
    },
    {
        "name": "HistorySage",
        "age": 10,
        "details": "A history buff AI that shares fascinating historical facts and insights.",
        "personality": "intellectual",
    },
    {
        "name": "AnimeSensei",
        "age": 5,
        "details": "An anime and manga enthusiast AI that recommends shows and discusses anime culture.",
        "personality": "otaku",
    },
    {
        "name": "BusinessStrategist",
        "age": 6,
        "details": "A business-savvy AI that provides guidance on startups, investments, and marketing.",
        "personality": "strategic",
    },
    {
        "name": "DarkMystic",
        "age": 8,
        "details": "An enigmatic AI that tells creepy stories, unsolved mysteries, and urban legends.",
        "personality": "mysterious",
    },
]


async def populate_ai_db():
    """
    Populate the AI database with dummy AI agents.
    """
    existing_ais = await ai_collection.count_documents({})
    if existing_ais > 0:
        print(
            f"AI database already contains {existing_ais} records. Skipping population."
        )
        return

    # Insert dummy AI agents
    result = await ai_collection.insert_many(dummy_ais)
    print(f"Inserted {len(result.inserted_ids)} AI agents into the database.")


if __name__ == "__main__":
    asyncio.run(populate_ai_db())
