# app/services/conversation_service.py

from app.repositories.conversation_repository import (
    create_conversation,
    get_conversation_by_id,
    list_conversations_for_user,
)
from app.models import ConversationCreate
from datetime import datetime
from fastapi import HTTPException, status
from app.repositories.user_repository import get_user_by_id
from typing import List


async def create_new_conversation(
    conversation: ConversationCreate, skip_participant_check: bool = False
) -> dict:
    """
    Create a new conversation.
    Verifies that every participant exists unless skip_participant_check is True.
    When skip_participant_check is True (for AI conversations), the AI participant is assumed valid.
    """
    conversation_data = conversation

    if not skip_participant_check:
        # Validate each participant exists in the users collection.
        for participant_id in conversation_data.get("participants", []):
            user = await get_user_by_id(participant_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with ID {participant_id} does not exist.",
                )
    conversation_data["created_at"] = datetime.utcnow()

    # Create the conversation in the database.
    return await create_conversation(conversation_data)


async def get_conversation(conversation_id: str) -> dict:
    """
    Retrieve a conversation by its ID. Raise an error if not found.
    """
    conversation = await get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found."
        )
    return conversation


async def list_user_conversations(user_id: str) -> list:
    """
    List all conversations for a given user.
    """
    return await list_conversations_for_user(user_id)


async def update_conversation_history_record(
    conversation_id: str, history: List[dict]
) -> dict:
    from app.repositories.conversation_repository import (
        update_conversation_history_record,
    )

    return await update_conversation_history_record(conversation_id, history)
