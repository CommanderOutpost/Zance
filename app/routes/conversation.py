"""
Conversation routes module.

Defines REST endpoints for conversation creation, retrieval, and listing.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from app.models import ConversationCreate, Conversation
from app.services.conversation_service import (
    create_new_conversation,
    get_conversation,
    list_user_conversations,
)

router = APIRouter()


@router.post("/", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation_endpoint(
    conversation: ConversationCreate,
) -> Dict[str, Any]:
    """
    Create a new conversation.

    :param conversation: A ConversationCreate instance.
    :return: The created conversation document.
    """
    try:
        return await create_new_conversation(conversation)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the conversation.",
        )


@router.get("/{conversation_id}")
async def get_conversation_endpoint(conversation_id: str) -> Dict[str, Any]:
    """
    Retrieve conversation details by its ID.

    :param conversation_id: The conversation ID.
    :return: A dictionary with conversation details.
    :raises HTTPException: If the conversation is not found.
    """
    conversation = await get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {
        "conversation_id": conversation_id,
        "participants": conversation.get("participants", []),
        "history": conversation.get("history", []),
    }


@router.get("/user/{user_id}", response_model=List[Conversation])
async def list_conversations_endpoint(user_id: str) -> List[Dict[str, Any]]:
    """
    List all conversations for a given user.

    :param user_id: The user's ID.
    :return: A list of conversation documents.
    """
    try:
        return await list_user_conversations(user_id)
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving conversations.",
        )
