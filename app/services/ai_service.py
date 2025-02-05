# app/services/ai_service.py

import openai
import asyncio
from app.config import settings
from app.services.redis_service import get_cached_value, set_cached_value

# Set your OpenAI API key from the configuration.
openai.api_key = settings.openai_api_key


async def get_ai_response(
    prompt: str, personality: str = "friendly", max_tokens: int = 150
) -> str:
    """
    Retrieve an AI-generated response for a given prompt, with caching.

    This function performs the following steps:
      1. Builds a full prompt that includes personality instructions.
      2. Checks Redis for a cached response based on a cache key derived from the prompt and personality.
      3. If found, returns the cached response.
      4. Otherwise, calls the OpenAI API to generate a response.
      5. Caches the response before returning it.

    :param prompt: The user input or conversation prompt.
    :param personality: The personality style for the AI (e.g., "friendly", "sarcastic").
    :param max_tokens: The maximum number of tokens for the response.
    :return: The AI-generated response as a string.
    """
    # Create a cache key based on personality and prompt.
    cache_key = f"ai_response:{personality}:{prompt}"

    # Check if the response is cached.
    cached_response = await get_cached_value(cache_key)
    if cached_response:
        return cached_response

    # Build the full prompt with personality instructions.
    full_prompt = f"You are a {personality} assistant.\nUser: {prompt}\nAI:"

    # Call the OpenAI API asynchronously (wrapping the synchronous call with asyncio.to_thread)
    response = await asyncio.to_thread(
        openai.Completion.create,
        engine="davinci",  # or "gpt-3.5-turbo" if available for completions
        prompt=full_prompt,
        max_tokens=max_tokens,
        temperature=0.7,
        n=1,
        stop=None,
    )

    # Extract the AI response text.
    ai_response = response.choices[0].text.strip()

    # Cache the response in Redis for future calls (default expiration is 1 hour)
    await set_cached_value(cache_key, ai_response, expire=3600)

    return ai_response
