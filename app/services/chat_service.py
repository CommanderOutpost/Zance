# app/services/chat_service.py

from app.repositories.chat_repository import save_message, get_conversation_messages
from app.models import Message


async def send_message(conversation_id: str, message: Message) -> dict:
    """
    Save a message to the conversation and return the saved document.
    """
    message_dict = message.dict()  # Convert Pydantic model to dict
    saved_message = await save_message(conversation_id, message_dict)
    return saved_message


async def fetch_conversation_history(conversation_id: str) -> list:
    """
    Retrieve the entire message history for a conversation.
    """
    return await get_conversation_messages(conversation_id)
