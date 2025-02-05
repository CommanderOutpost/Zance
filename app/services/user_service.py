# app/services/user_service.py

import logging
from app.models import UserCreate
from app.repositories.user_repository import (
    get_user_by_username,
    create_user,
    get_all_users,
)
from app.utils.password import hash_password, verify_password
from app.utils.auth import create_access_token
from fastapi import HTTPException, status
from datetime import datetime

# Configure logging
logger = logging.getLogger("user_service")
logger.setLevel(logging.INFO)


async def register_user(user: UserCreate) -> dict:
    """
    Register a new user:
      - Ensure the username is unique.
      - Hash the password.
      - Create the user in the database.
    """
    try:
        # Check if username exists
        existing_user = await get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists.",
            )
        # Prepare new user data
        new_user = {
            "username": user.username,
            "password": hash_password(user.password),
            "created_at": datetime.now(datetime.timezone.utc)(),
        }
        created_user = await create_user(new_user)
        logger.info(f"User '{user.username}' registered successfully.")
        return created_user
    except HTTPException:
        # Reraise known HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error registering user '{user.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration.",
        )


async def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate the user:
      - Retrieve the user from the database.
      - Verify the password.
      - Generate and return a JWT token if credentials are valid.
    """
    try:
        stored_user = await get_user_by_username(username)
        if not stored_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
            )
        if not verify_password(password, stored_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
            )
        token_payload = {
            "sub": str(stored_user["_id"]),
            "username": stored_user["username"],
        }
        token = create_access_token(token_payload)
        logger.info(f"User '{username}' authenticated successfully.")
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during authentication for user '{username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication.",
        )


async def get_users():
    """
    Retrieve all users from the database.
    """
    try:
        users = await get_all_users()
        return users
    except Exception as e:
        print(e)
        logger.error(f"Error retrieving all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving users.",
        )
