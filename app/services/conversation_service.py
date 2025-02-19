"""
Conversation service module.

Implements business logic for conversation creation, retrieval, listing, and history updates.
"""

from typing import List, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from app.models import ConversationCreate
from app.repositories.conversation_repository import (
    create_conversation,
    get_conversation_by_id,
    list_conversations_for_user,
    update_conversation_history_record as update_conversation_history_record_repo,
)
from app.repositories.user_repository import get_user_by_id
from app.repositories.ai_repository import get_ai_by_id
import logging

logger = logging.getLogger("conversation_service")
logger.setLevel(logging.INFO)


async def create_new_conversation(
    conversation: ConversationCreate, skip_participant_check: bool = False
) -> Dict[str, Any]:
    """
    Create a new conversation.

    For group chats that include both users and AI agents, each participant is verified
    to exist either in the users collection or the AI collection (unless skip_participant_check is True).

    :param conversation: A ConversationCreate instance containing conversation data.
    :param skip_participant_check: If True, bypasses participant verification.
    :return: The created conversation document.
    :raises HTTPException: If a participant ID is invalid or does not exist.
    """
    # Convert the Pydantic model to a dictionary.
    conversation_data: Dict[str, Any] = conversation

    if not skip_participant_check:
        for participant_id in conversation_data.get("participants", []):
            user = await get_user_by_id(participant_id)
            if not user:
                ai = await get_ai_by_id(participant_id)
                if not ai:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Participant with ID {participant_id} does not exist.",
                    )
    conversation_data["created_at"] = datetime.utcnow()
    logger.info(
        f"Creating conversation with participants: {conversation_data.get('participants')}"
    )
    return await create_conversation(conversation_data)


async def get_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    Retrieve a conversation by its ID.

    :param conversation_id: The conversation ID as a string.
    :return: The conversation document.
    :raises HTTPException: If the conversation is not found.
    """
    conversation = await get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found."
        )
    return conversation


async def list_user_conversations(user_id: str) -> List[Dict[str, Any]]:
    """
    List all conversations for a given user.

    :param user_id: The user's ID.
    :return: A list of conversation documents.
    """
    return await list_conversations_for_user(user_id)


async def update_conversation_history_record(
    conversation_id: str, history: List[Dict[str, Any]], interrupted: bool = False
) -> Dict[str, Any]:
    """
    Update a conversation's history field (and optionally its interrupted status).
    """

    # Call the repository function with both history and interrupted
    return await update_conversation_history_record_repo(
        conversation_id, history, interrupted
    )
