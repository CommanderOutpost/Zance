"""
AI Service Module

Implements business logic for generating AI responses using the OpenAI client.
Handles caching via Redis and input validation.
"""

import asyncio
from typing import List, Dict, Any
from openai import OpenAI
from app.config import settings
from app.services.redis_service import get_cached_value, set_cached_value
from fastapi import HTTPException, status
from app.services.prompts.master_system_prompt import get_master_system_prompt

# Initialize the OpenAI client with the API key from settings.
openai_client = OpenAI(api_key=settings.openai_api_key)
openai_model = settings.openai_model


async def get_ai_response(
    prompt: str, conversation_history: List[Dict[str, Any]], model: str = openai_model
) -> str:
    """
    Generate an AI response using the OpenAI client.

    :param prompt: The user's input message.
    :param conversation_history: A list of dictionaries representing the conversation history.
                                 Each dictionary must contain 'role' and 'content' keys.
    :param model: The AI model to use (default is set in configuration).
    :return: The AI's response as a string.
    :raises ValueError: If inputs are invalid.
    :raises HTTPException: If the OpenAI API call fails.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("The 'prompt' parameter must be a non-empty string.")
    if not isinstance(conversation_history, list) or not all(
        isinstance(msg, dict) and "role" in msg and "content" in msg
        for msg in conversation_history
    ):
        raise ValueError(
            "The 'conversation_history' must be a list of dictionaries with 'role' and 'content' keys."
        )

    # Create a cache key for this AI response.
    cache_key = f"ai_response:{model}:{prompt}:{str(conversation_history)}"
    cached_response = await get_cached_value(cache_key)
    if cached_response:
        return cached_response

    def sync_call(conversation_history):
        return openai_client.chat.completions.create(
            model=openai_model,
            messages=conversation_history,
        )

    try:
        response = await asyncio.to_thread(sync_call, conversation_history)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI response: {e}",
        )

    ai_response = response.choices[0].message.content.strip()
    # Append the AI response to the conversation history.
    conversation_history.append({"role": "assistant", "content": ai_response})
    # Cache the response.
    await set_cached_value(cache_key, ai_response, expire=3600)
    return ai_response


async def master_ai(
    prompt: str,
    user_data: Dict[str, Any],
    ai_data,
    conversation_history: List[Dict[str, Any]],
) -> str:
    """
    Generate a description of what the AI will do in the action step

    :param prompt: The user's input message.
    :param user_data: The user's data.
    :param ai_data: The AI's data.

    :return: The AI's response as a string.
    """

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("The 'prompt' parameter must be a non-empty string.")
    if not isinstance(conversation_history, list) or not all(
        isinstance(msg, dict) and "role" in msg and "content" in msg
        for msg in conversation_history
    ):
        raise ValueError(
            "The 'conversation_history' must be a list of dictionaries with 'role' and 'content' keys."
        )

    master_system_prompt = get_master_system_prompt(
        user_data, ai_data, conversation_history
    )

    def sync_call():
        return openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": master_system_prompt},
                {
                    "role": "user",
                    "content": f"User latest message:{prompt}\nYour thoughts:\n",
                },
            ],
            temperature=0.7,
        )

    try:
        response = await asyncio.to_thread(sync_call)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI response: {e}",
        )

    return response
