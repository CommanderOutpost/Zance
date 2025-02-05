# app/repositories/conversation_repository.py

from app.database import db
from typing import List
from bson import ObjectId


async def create_conversation(conversation_data: dict) -> dict:
    """
    Insert a new conversation into the database and return the created document.
    """
    result = await db.conversations.insert_one(conversation_data)
    conversation_data["_id"] = str(result.inserted_id)
    return conversation_data


async def get_conversation_by_id(conversation_id: str) -> dict:
    """
    Retrieve a conversation by its ID.
    """
    conversation = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
    if conversation:
        conversation["_id"] = str(conversation["_id"])
    return conversation


async def list_conversations_for_user(user_id: str) -> List[dict]:
    """
    List all conversations that include the given user_id in the participants.
    """
    cursor = db.conversations.find({"participants": user_id}).sort("created_at", -1)
    conversations = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        conversations.append(doc)
    return conversations
