"""
AI Repository Module

Provides functions to interact with the "ais" collection in MongoDB.
"""

from typing import Dict, Any, List, Optional
from app.database import db
from bson import ObjectId, errors
from fastapi import HTTPException, status


async def create_ai(ai_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert a new AI agent into the database and return the created document.

    :param ai_data: A dictionary containing AI agent data.
    :return: The inserted AI document with _id as a string.
    """
    result = await db.ais.insert_one(ai_data)
    ai_data["_id"] = str(result.inserted_id)
    return ai_data


async def get_ai_by_id(ai_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve an AI agent by its ID.

    :param ai_id: The AI agent's ID as a 24-character hex string.
    :return: The AI document if found; otherwise, None.
    :raises HTTPException: If the AI id is invalid.
    """
    try:
        oid = ObjectId(ai_id)
    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid AI id: {ai_id}. It must be a 24-character hex string.",
        )
    ai = await db.ais.find_one({"_id": oid})
    if ai:
        ai["_id"] = str(ai["_id"])
    return ai


async def list_all_ais() -> List[Dict[str, Any]]:
    """
    List all AI agents in the database.

    :return: A list of AI documents with _id converted to strings.
    """
    ais = await db.ais.find().to_list(length=None)
    for ai in ais:
        ai["_id"] = str(ai["_id"])
    return ais


async def update_ai(ai_id: str, ai_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing AI agent.

    :param ai_id: The ID of the AI agent.
    :param ai_data: A dictionary containing the fields to update.
    :return: The updated AI document.
    :raises HTTPException: If the AI is not found or the ID is invalid.
    """
    try:
        oid = ObjectId(ai_id)
    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid AI id: {ai_id}. It must be a 24-character hex string.",
        )
    result = await db.ais.update_one({"_id": oid}, {"$set": ai_data})
    if result.modified_count:
        return await get_ai_by_id(ai_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI not found."
        )


async def delete_ai(ai_id: str) -> Dict[str, Any]:
    """
    Delete an AI agent from the database.

    :param ai_id: The AI agent's ID.
    :return: A dictionary with a deletion message.
    :raises HTTPException: If the AI is not found or the ID is invalid.
    """
    try:
        oid = ObjectId(ai_id)
    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid AI id: {ai_id}. It must be a 24-character hex string.",
        )
    result = await db.ais.delete_one({"_id": oid})
    if result.deleted_count:
        return {"detail": "AI deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI not found."
        )
