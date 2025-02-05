# app/services/redis_pubsub.py

import json
from app.config import settings
import redis.asyncio as redis
from datetime import datetime

# Create a shared async Redis client.
redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


# Function to serialize datetime objects
def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to string
    raise TypeError(f"Type {type(obj)} not serializable")


async def publish_message(channel: str, message: dict):
    """
    Publish a JSON message to a Redis channel.
    """
    # Convert message to JSON and handle datetime serialization
    message_json = json.dumps(message, default=json_serializer)
    await redis_client.publish(channel, message_json)


async def subscribe_to_channel(channel: str):
    """
    Subscribe to a Redis channel and yield messages as they come in.
    Use this in an async loop.
    """
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    try:
        async for message in pubsub.listen():
            # Redis sends several message types; we only care about messages of type "message"
            if message["type"] == "message":
                try:
                    yield json.loads(message["data"])
                except Exception:
                    continue
    finally:
        await pubsub.unsubscribe(channel)
