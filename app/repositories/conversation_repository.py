"""
Conversation repository module.

Handles direct interactions with the "conversations" collection in MongoDB.
"""

from typing import List, Dict, Any
from app.database import db
from bson import ObjectId, errors
from fastapi import HTTPException, status


async def create_conversation(conversation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert a new conversation into the database.

    :param conversation_data: A dictionary containing conversation data.
    :return: The inserted conversation document with the _id converted to a string.
    """
    result = await db.conversations.insert_one(conversation_data)
    conversation_data["_id"] = str(result.inserted_id)
    return conversation_data


async def get_conversation_by_id(conversation_id: str) -> Dict[str, Any]:
    """
    Retrieve a conversation from the database by its ID.

    :param conversation_id: The conversation ID as a 24-character hex string.
    :return: The conversation document if found; otherwise, None.
    """
    try:
        oid = ObjectId(conversation_id)
    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation id: {conversation_id}. It must be a 24-character hex string.",
        )
    conversation = await db.conversations.find_one({"_id": oid})
    if conversation:
        conversation["_id"] = str(conversation["_id"])
    return conversation


async def list_conversations_for_user(user_id: str) -> List[Dict[str, Any]]:
    """
    List all conversations that include the given user ID in their participants.

    :param user_id: The user ID as a string.
    :return: A list of conversation documents.
    """
    cursor = db.conversations.find({"participants": user_id}).sort("created_at", -1)
    conversations: List[Dict[str, Any]] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        conversations.append(doc)
    return conversations


async def update_conversation_history_record(
    conversation_id: str, history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Update the history field of a conversation document.

    :param conversation_id: The conversation ID.
    :param history: A list of message dictionaries to set as the conversation history.
    :return: The updated conversation document.
    :raises HTTPException: If the conversation ID is invalid or the conversation is not found.
    """
    try:
        oid = ObjectId(conversation_id)
    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation id: {conversation_id}. It must be a 24-character hex string.",
        )
    result = await db.conversations.update_one(
        {"_id": oid}, {"$set": {"history": history}}
    )
    if result.modified_count:
        updated_conversation = await get_conversation_by_id(conversation_id)
        return updated_conversation
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found."
        )
