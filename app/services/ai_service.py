# app/services/ai_service.py

import asyncio
from openai import OpenAI
from app.config import settings
from app.services.redis_service import get_cached_value, set_cached_value

# Initialize the OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key)

openai_model = settings.openai_model


async def get_ai_response(
    prompt: str, conversation_history: list, model: str = openai_model
) -> str:
    """
    Generates an AI response using the OpenAI client, given a prompt and conversation history.

    Parameters:
        prompt (str): The user's input message to the AI.
        conversation_history (list): List of dictionaries representing the conversation history.
                                     Each dictionary must contain 'role' and 'content' keys.
        model (str): The AI model to use (default is "gpt-4o-mini").

    Returns:
        str: AI's response message.
    """
    # Validate input
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("The 'prompt' parameter must be a non-empty string.")
    if not isinstance(conversation_history, list) or not all(
        isinstance(msg, dict) and "role" in msg and "content" in msg
        for msg in conversation_history
    ):
        raise ValueError(
            "The 'conversation_history' must be a list of dictionaries with 'role' and 'content' keys."
        )

    # Create a cache key based on model, prompt, and conversation history.
    cache_key = f"ai_response:{model}:{prompt}:{str(conversation_history)}"
    cached_response = await get_cached_value(cache_key)
    if cached_response:
        return cached_response

    # Call the OpenAI API asynchronously using asyncio.to_thread
    def sync_call():
        return openai_client.chat.completions.create(
            model=model,
            messages=conversation_history,
        )

    response = await asyncio.to_thread(sync_call)
    ai_response = response.choices[0].message.content.strip()

    # Append the AI's response to the conversation history.
    conversation_history.append({"role": "assistant", "content": ai_response})

    # Cache the response
    await set_cached_value(cache_key, ai_response, expire=3600)
    return ai_response
