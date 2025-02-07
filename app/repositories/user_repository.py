"""
User repository module.

Provides functions for querying and updating the "users" collection in MongoDB.
"""

from typing import Optional, List, Dict
from app.database import db
from bson import ObjectId, errors
from fastapi import HTTPException, status


async def get_user_by_username(username: str) -> Optional[Dict]:
    """
    Retrieve a user document by username.

    :param username: The username to search for.
    :return: The user document if found, otherwise None.
    """
    return await db.users.find_one({"username": username})


async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Retrieve a user document by its ID.
    Validates the ID format; raises a 400 error if invalid.

    :param user_id: The user ID as a string.
    :return: The user document if found, otherwise None.
    :raises HTTPException: If the user_id is not a valid 24-character hex string.
    """
    try:
        oid = ObjectId(user_id)
    except errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user id: {user_id}. It must be a 24-character hex string.",
        )

    user = await db.users.find_one({"_id": oid})
    if user:
        user["_id"] = str(user["_id"])
    return user


async def create_user(user_data: Dict) -> Dict:
    """
    Insert a new user document into the database.

    :param user_data: A dictionary containing user data.
    :return: The created user document with the _id converted to a string.
    """
    result = await db.users.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return user_data


async def get_all_users() -> List[Dict]:
    """
    Retrieve all user documents from the database,
    converting each document's _id to a string.

    :return: A list of user documents.
    """
    users = await db.users.find().to_list(length=None)
    for user in users:
        user["_id"] = str(user["_id"])
    return users
