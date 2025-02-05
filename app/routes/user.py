# app/routes/user.py

from fastapi import APIRouter
from app.models import UserCreate, UserResponse
from app.services.user_service import register_user, authenticate_user
from pydantic import BaseModel

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(user: UserCreate):
    """
    Endpoint to register a new user.
    """
    return await register_user(user)


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(user: UserLogin):
    """
    Endpoint for user login that returns a JWT on successful authentication.
    """
    return await authenticate_user(user.username, user.password)
