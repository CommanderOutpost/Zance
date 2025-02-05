# app/models.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ---------------------------------
# User Models
# ---------------------------------


class UserCreate(BaseModel):
    """
    Model for user sign-up requests.
    """

    username: str = Field(..., example="john_doe")
    password: str = Field(..., min_length=6, example="securepass123")


class UserResponse(BaseModel):
    """
    Model for returning user data.
    """

    id: str = Field(..., alias="_id")
    username: str
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


# ---------------------------------
# Chat Message Models
# ---------------------------------


class Message(BaseModel):
    """
    Model for chat messages.
    """

    sender: str = Field(..., example="john_doe")
    content: str = Field(..., example="Hello, how are you?")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


# ---------------------------------
# Additional Models (if needed)
# ---------------------------------

# You can define other models here, for example, models for login, or for updating profiles.
