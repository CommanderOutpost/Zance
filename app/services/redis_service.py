# app/services/redis_service.py

import json
from app.config import settings
import redis.asyncio as redis

# Create an async Redis client using the URL from your configuration.
redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


async def get_cached_value(key: str):
    """
    Retrieve a cached value from Redis using the provided key.

    :param key: The Redis key for the cached value.
    :return: The cached value, or None if not found.
    """
    value = await redis_client.get(key)
    if value is not None:
        try:
            # Attempt to load the value from JSON if possible.
            return json.loads(value)
        except json.JSONDecodeError:
            # If not JSON, return the raw string.
            return value
    return None


async def set_cached_value(key: str, value, expire: int = 3600):
    """
    Cache a value in Redis with an optional expiration time (default is 3600 seconds / 1 hour).

    :param key: The Redis key under which the value will be stored.
    :param value: The value to cache. If not a string, it will be converted to JSON.
    :param expire: Expiration time in seconds.
    """
    # Convert the value to JSON if it's not already a string.
    if not isinstance(value, str):
        value = json.dumps(value)
    await redis_client.set(key, value, ex=expire)


async def delete_cached_value(key: str):
    """
    Delete a value from Redis using the provided key.

    :param key: The Redis key to delete.
    """
    await redis_client.delete(key)
