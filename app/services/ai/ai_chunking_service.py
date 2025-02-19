"""
AI Chunking Service

Uses an LLM (OpenAI) to determine how to schedule or delay AI responses
to make conversation more realistic.

Warning: Relying heavily on an LLM for scheduling can rack up tokens/cost. 
Also, parsing JSON from an LLM can break if the LLM doesn’t follow instructions. 
You might want to add robust error handling or a "Retry with stricter instructions" approach.
"""

import asyncio
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from app.services.redis_service import get_cached_value, set_cached_value
from openai import OpenAI
from app.services.prompts.chunking_system_prompt import (
    get_chunking_system_prompt,
    generate_content_prompt,
)
import json
import re
import ast

from app.config import settings

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key)


def extract_json_list_from_text(text: str) -> Optional[str]:
    """
    Extracts a JSON array from a string robustly and ensures valid JSON formatting.
    Args:
        text (str): The text containing JSON.
    Returns:
        Optional[str]: Extracted JSON array as a string or None if extraction fails.
    """
    try:
        text = text.strip()
        # Check for JSON inside triple backticks
        code_block_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if code_block_match:
            json_text = code_block_match.group(1).strip()
        else:
            # Extract JSON-like text from the response
            json_match = re.search(r"(\[.*?\])", text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1).strip()
            else:
                return None  # No JSON found

        # Attempt to convert the JSON-like text to a Python object using ast.literal_eval,
        # which can handle single quotes correctly.
        try:
            data = ast.literal_eval(json_text)
        except Exception as e:
            return None

        # Convert the Python object back to a valid JSON string
        valid_json = json.dumps(data)
        return valid_json

    except Exception:
        return None


async def chunk_messages(
    conversation_history: List[Dict[str, Any]],
    user_data: Dict[str, Any],
    ai_data: Dict,
    user_prompt,
    master_decision: str,
) -> Dict[str, Any]:
    """
    Determine a scheduling plan (chunked responses + timing) using an LLM.

    :param conversation_history: List of messages (role, content).
    :param user_data: Dictionary with info about the user (could be used in the prompt).
    :param ai_personality: Personality or extra details about the AI.
    :return: A list like:
        [
            {
              "content": str,
              "delay_seconds": float
            },
            ...
        ],
    """

    # Cache key can be based on the entire conversation + user_data
    cache_key = (
        f"scheduling_plan:{str(conversation_history)}:{str(user_data)}:{str(ai_data)}"
    )
    cached_plan = await get_cached_value(cache_key)
    if cached_plan:
        return cached_plan

    print("userdata", user_data)

    chunking_system_prompt = get_chunking_system_prompt()
    content_prompt = generate_content_prompt(
        user_prompt, user_data, ai_data, master_decision, conversation_history
    )

    def sync_llm_call():
        return openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": chunking_system_prompt},
                {
                    "role": "user",
                    "content": content_prompt,
                },
            ],
            temperature=0.7,
        )

    try:
        response = await asyncio.to_thread(sync_llm_call)
        print(response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to chunk messages: {e}",
        )

    # Parse AI response.
    raw_text = extract_json_list_from_text(response.choices[0].message.content)

    try:
        scheduling_plan = json.loads(raw_text)
    except json.JSONDecodeError:
        # If it fails, we fallback to a default or raise an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chunks is not valid JSON. LLM returned: " + raw_text,
        )

    # Store in cache
    await set_cached_value(cache_key, scheduling_plan, expire=3600)
    return scheduling_plan
