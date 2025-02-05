# app/repositories/user_repository.py

from app.database import db
from bson import ObjectId, errors
from fastapi import HTTPException, status


async def get_user_by_username(username: str):
    """
    Retrieve a user from the database by username.
    """
    return await db.users.find_one({"username": username})


async def get_user_by_id(user_id: str):
    """
    Retrieve a user from the database by user ID.
    If the user_id is not a valid ObjectId, raises an HTTP 400 error.
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


async def create_user(user_data: dict) -> dict:
    """
    Insert a new user into the database and return the created document.
    """
    result = await db.users.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return user_data


async def get_all_users():
    """
    Retrieve all users from the database.
    Convert the ObjectId of each user to a string.
    """
    users = await db.users.find().to_list(None)
    for user in users:
        user["_id"] = str(user["_id"])
    return users
