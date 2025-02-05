# app/services/conversation_service.py

from app.repositories.conversation_repository import (
    create_conversation,
    get_conversation_by_id,
    list_conversations_for_user,
)
from app.models import ConversationCreate
from datetime import datetime
from fastapi import HTTPException, status


async def create_new_conversation(conversation: ConversationCreate) -> dict:
    """
    Create a new conversation. Automatically adds the current timestamp.
    """
    conversation_data = conversation.dict()
    conversation_data["created_at"] = datetime.utcnow()

    # Optionally, you might want to add logic here to ensure that a DM between the same users is unique.
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
