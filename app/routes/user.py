# app/routes/user.py

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
    Endpoint to register a new user.
    """
    try:
        created_user = await register_user(user)
        return created_user
    except HTTPException as he:
        raise he
    except Exception as e:
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
    Endpoint for user login that returns a JWT on successful authentication.
    """
    try:
        token_data = await authenticate_user(user.username, user.password)
        return token_data
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during user login.",
        )


@router.get("/all")
async def get_all_users_endpoint():
    """
    Endpoint to retrieve all users.
    """
    try:
        users = await get_all_users_service()
        return users
    except HTTPException as he:
        raise he
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving users.",
        )
