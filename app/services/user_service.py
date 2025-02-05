# app/services/user_service.py
from app.models import UserCreate
from app.repositories.user_repository import get_user_by_username, create_user
from app.utils.password import hash_password, verify_password
from app.utils.auth import create_access_token
from fastapi import HTTPException, status


async def register_user(user: UserCreate) -> dict:
    # Check for existing user
    if await get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # Hash the password and create user data
    new_user = {
        "username": user.username,
        "password": hash_password(user.password),
        "created_at": __import__("datetime").datetime.utcnow(),
    }
    return await create_user(new_user)


async def authenticate_user(username: str, password: str) -> dict:
    stored_user = await get_user_by_username(username)
    if not stored_user or not verify_password(password, stored_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Create token payload and generate access token
    token_payload = {
        "sub": str(stored_user["_id"]),
        "username": stored_user["username"],
    }
    token = create_access_token(token_payload)
    return {"access_token": token, "token_type": "bearer"}
