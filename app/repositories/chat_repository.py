# app/repositories/chat_repository.py

from app.database import db
from typing import List


async def save_message(conversation_id: str, message_data: dict) -> dict:
    """
    Save a chat message to the 'messages' collection.
    The message_data should include sender, content, and timestamp.
    The conversation_id is added to the document.
    """
    # Attach conversation_id to the message document.
    message_data["conversation_id"] = conversation_id
    result = await db.messages.insert_one(message_data)
    message_data["_id"] = str(result.inserted_id)
    return message_data


async def get_conversation_messages(conversation_id: str) -> List[dict]:
    """
    Retrieve all messages for a given conversation_id, sorted by timestamp.
    """
    cursor = db.messages.find({"conversation_id": conversation_id}).sort("timestamp", 1)
    messages = []
    async for document in cursor:
        # Convert the MongoDB ObjectId to a string.
        document["_id"] = str(document["_id"])
        messages.append(document)
    return messages
