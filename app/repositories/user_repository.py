# app/repositories/user_repository.py
from app.database import db


async def get_user_by_username(username: str):
    return await db.users.find_one({"username": username})


async def create_user(user_data: dict) -> dict:
    result = await db.users.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return user_data
