# app/routes/conversation.py

from fastapi import APIRouter, HTTPException, status
from app.models import ConversationCreate, Conversation
from app.services.conversation_service import (
    create_new_conversation,
    get_conversation,
    list_user_conversations,
)
from typing import List

router = APIRouter()


@router.post("/", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation_endpoint(conversation: ConversationCreate):
    """
    Endpoint to create a new conversation.
    """
    return await create_new_conversation(conversation)


@router.get("/{conversation_id}")
async def get_conversation_endpoint(conversation_id: str):
    """
    Endpoint to retrieve conversation details by its ID, ensuring AI responses are included.
    """
    conversation = await get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return {
        "conversation_id": conversation_id,
        "participants": conversation.get("participants", []),
        "history": conversation.get("history", []),  # Ensure latest AI responses appear
    }


@router.get("/user/{user_id}", response_model=List[Conversation])
async def list_conversations_endpoint(user_id: str):
    """
    Endpoint to list all conversations for a given user.
    """
    return await list_user_conversations(user_id)
