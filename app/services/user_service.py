"""
User Service Module

Handles business logic for user registration, authentication, and retrieval.
Now uses the phone number as the unique identifier; the username is no longer required to be unique.
"""

import logging
from datetime import datetime
from fastapi import HTTPException, status
from app.models import UserCreate
from app.repositories.user_repository import (
    get_user_by_phone_number,
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
      - Check if the phone number is already registered (uniqueness check).
      - Hash the password.
      - Save the new user to the database.

    :param user: A UserCreate instance containing user signup data.
    :return: The created user document.
    :raises HTTPException: If the phone number is already in use or registration fails.
    """
    try:
        # Check if phone number already exists
        existing_user = await get_user_by_phone_number(user.phone_number)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered.",
            )
        new_user = {
            "username": user.username,
            "password": hash_password(user.password),
            "phone_number": user.phone_number,
            "created_at": datetime.utcnow(),
        }
        created_user = await create_user(new_user)
        logger.info(f"User with phone {user.phone_number} registered successfully.")
        return created_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user with phone {user.phone_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration.",
        )


async def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate a user:
      - Retrieve the user by username (username is not unique, so this should ideally use phone number instead).
      - Verify the password.
      - Generate a JWT token on success.

    NOTE: If you want to authenticate using phone numbers instead, modify this function accordingly.

    :param username: The username.
    :param password: The user's password.
    :return: A dictionary containing the access token and token type.
    :raises HTTPException: If authentication fails.
    """
    # (This function uses username for now. You could add a phone-based authentication if needed.)
    from app.repositories.user_repository import get_user_by_username

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
