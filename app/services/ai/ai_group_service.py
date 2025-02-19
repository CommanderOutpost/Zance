"""
Module: app.services.ai_group_service

This module implements the automated AI response logic for group chats.
It retrieves participant names (from either the user or AI collections),
builds a system prompt that informs the AI of its identity and the group context,
and then generates an AI response to the latest user message.
"""

import logging
from typing import List, Optional, Dict, Any

from app.services.conversation_service import (
    get_conversation,
    update_conversation_history_record,
)
from app.services.ai.ai_service import get_ai_response
from app.repositories.user_repository import get_user_by_id
from app.repositories.ai_repository import get_ai_by_id as get_ai_by_id_repo
from app.config import settings
import sys

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add handler if missing
if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


async def get_participant_names(participants: List[str]) -> List[str]:
    """
    Given a list of participant IDs, return their display names.

    Tries to retrieve each participant as a user first; if not found, then as an AI.
    If a participant cannot be found in either collection, its ID is returned.

    :param participants: A list of participant IDs (strings).
    :return: A list of display names corresponding to the participant IDs.
    """
    names: List[str] = []
    for pid in participants:
        name: Optional[str] = None
        # Try as user
        try:
            user = await get_user_by_id(pid)
            if user:
                name = user.get("username")
                logger.debug(f"Found user for {pid}: {name}")
        except Exception as e:
            logger.debug(f"Error fetching user for {pid}: {e}")
        # Try as AI if not found as user
        if not name:
            try:
                ai = await get_ai_by_id_repo(pid)
                if ai:
                    name = ai.get("name")
                    logger.debug(f"Found AI for {pid}: {name}")
            except Exception as e:
                logger.debug(f"Error fetching AI for {pid}: {e}")
        names.append(name if name else pid)
        logger.debug(f"Current participant names list: {names}")
    return names


async def automate_group_ai_response(conversation_id: str) -> Optional[Dict[str, Any]]:
    """
    Automatically generate an AI response for a group chat conversation.

    The function performs the following steps:
      1. Loads the conversation and verifies that it is a group chat.
      2. Retrieves participant names and identifies the AI agent in the group.
      3. Constructs a system prompt incorporating the AI's identity and group context.
      4. Extracts the latest user message (and sender) from the conversation history.
      5. Constructs an input prompt for the AI (including the sender's name).
      6. Generates an AI response using the OpenAI client.
      7. Appends the AI response to the conversation history and updates the database record.

    :param conversation_id: The conversation ID as a string.
    :return: The updated conversation document if successful, otherwise None.
    :raises Exception: If the AI response generation fails.
    """
    logger.info(f"Automating group AI response for conversation: {conversation_id}")
    conversation = await get_conversation(conversation_id)
    if not conversation or conversation.get("conversation_type") != "group":
        logger.debug(
            "Conversation is not a group chat or not found; skipping AI response."
        )
        return None

    history: List[Dict[str, Any]] = conversation.get("history", [])
    participants: List[str] = conversation.get("participants", [])

    # Identify the AI in the group chat (assumes at most one AI)
    ai_id: Optional[str] = None
    for pid in participants:
        try:
            ai = await get_ai_by_id_repo(pid)
            if ai:
                ai_id = pid
                logger.debug(f"AI found in conversation: {ai.get('name', 'AI')}")
                break
        except Exception as e:
            logger.debug(f"Error checking AI for participant {pid}: {e}")

    # Retrieve display names for all participants
    names = await get_participant_names(participants)
    logger.debug(f"Participant names: {names}")

    # Build the group system prompt, including AI identity if available
    if ai_id:
        ai_details = await get_ai_by_id_repo(ai_id)
        ai_name = ai_details.get("name", "AI")
        ai_personality = ai_details.get("personality", "friendly")
        ai_description = ai_details.get("details", "An AI assistant.")
        group_prompt = (
            f"You are {ai_name}, an AI participant in this group chat. "
            f"Your personality is {ai_personality}. {ai_description} "
            f"Participants: {', '.join(names)}. "
            f"Respond appropriately in character."
        )
    else:
        group_prompt = f"This is a group chat with participants: {', '.join(names)}. Please respond appropriately."
        logger.debug(f"Group prompt (no AI identity): {group_prompt}")

    # Ensure the system prompt is in the conversation history (update or insert)
    if not any(msg.get("role") == "system" for msg in history):
        history.insert(0, {"role": "system", "content": group_prompt})
    else:
        for idx, msg in enumerate(history):
            if msg.get("role") == "system":
                history[idx] = {"role": "system", "content": group_prompt}
                break

    # Extract the latest user message and sender from the conversation history
    last_message: Optional[str] = None
    last_user_sender: Optional[str] = None
    for msg in reversed(history):
        if msg.get("role") == "user":
            last_message = msg.get("content", "").strip()
            last_user_sender = msg.get("sender")
            break

    if not last_message:
        logger.debug("No valid user message found. Skipping AI response.")
        return None  # Nothing to respond to

    # Build the input prompt, including sender's name if available
    if last_user_sender:
        ai_input = f"As {ai_name}, respond to this group chat message from {last_user_sender}: {last_message}"
    else:
        ai_input = f"As {ai_name}, respond to this group chat message: {last_message}"
    logger.debug(f"AI input prompt: {ai_input}")

    # Generate the AI response
    try:
        ai_response = await get_ai_response(
            ai_input, history, model=settings.openai_model
        )
        logger.info(f"Generated AI response: {ai_response}")
    except Exception as e:
        raise Exception(f"Failed to generate group AI response: {e}")

    # Append the AI response to the conversation history
    history.append({"role": "assistant", "content": ai_response})
    updated_conversation = await update_conversation_history_record(
        conversation_id, history
    )
    logger.info("Conversation history updated with AI response.")
    return updated_conversation
