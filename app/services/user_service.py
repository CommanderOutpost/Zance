"""
User service module.

Handles business logic for user registration, authentication, and retrieval.
"""

import logging
from datetime import datetime
from fastapi import HTTPException, status
from app.models import UserCreate
from app.repositories.user_repository import (
    get_user_by_username,
    create_user,
    get_all_users,
)
from app.utils.password import hash_password, verify_password
from app.utils.auth import create_access_token

logger = logging.getLogger("user_service")
logger.setLevel(logging.INFO)


async def register_user(user: UserCreate) -> dict:
    """
    Register a new user:
      - Check if the username already exists.
      - Hash the password.
      - Save the new user to the database.

    :param user: A UserCreate instance containing user signup data.
    :return: The created user document.
    :raises HTTPException: If the username is already taken or if registration fails.
    """
    try:
        existing_user = await get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists.",
            )
        new_user = {
            "username": user.username,
            "password": hash_password(user.password),
            "created_at": datetime.utcnow(),
        }
        created_user = await create_user(new_user)
        logger.info(f"User '{user.username}' registered successfully.")
        return created_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user '{user.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration.",
        )


async def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate a user:
      - Retrieve the user by username.
      - Verify the password.
      - Generate a JWT token on success.

    :param username: The username.
    :param password: The user's password.
    :return: A dictionary containing the access token and token type.
    :raises HTTPException: If authentication fails.
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


async def get_users() -> list:
    """
    Retrieve all users.

    :return: A list of user documents.
    :raises HTTPException: If user retrieval fails.
    """
    try:
        users = await get_all_users()
        return users
    except Exception as e:
        logger.error(f"Error retrieving all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving users.",
        )
