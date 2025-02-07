"""
User Routes Module

Defines endpoints for user signup, login, and retrieval.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import UserCreate, UserResponse
from app.services.user_service import (
    register_user,
    authenticate_user,
    get_users as get_all_users_service,
)
from pydantic import BaseModel

router = APIRouter()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(user: UserCreate):
    """
    Register a new user.

    :param user: A UserCreate model instance containing user signup data.
    :return: The created user document.
    """
    try:
        created_user = await register_user(user)
        return created_user
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during user registration.",
        )


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(user: UserLogin):
    """
    Authenticate a user and return a JWT token.

    :param user: A UserLogin model instance.
    :return: A dictionary with access_token and token_type.
    """
    try:
        token_data = await authenticate_user(user.username, user.password)
        return token_data
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during user login.",
        )


@router.get("/all")
async def get_all_users_endpoint():
    """
    Retrieve all users.

    :return: A list of user documents.
    """
    try:
        users = await get_all_users_service()
        return users
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving users.",
        )
