# app/models.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List

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
        from_attributes = True
        populate_by_name = True


# ---------------------------------
# Chat Message Models
# ---------------------------------


class Message(BaseModel):
    """
    Model for chat messages.
    """

    sender: str = Field(..., example="john_doe")
    content: str = Field(..., example="Hello, how are you?")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.utcnow())

    class Config:
        from_attributes = True


# ---------------------------------
# Conversation Models
# ---------------------------------


class ConversationCreate(BaseModel):
    """
    Model for creating a new conversation.
    """

    participants: List[str] = Field(..., example=["user_id_1", "user_id_2"])
    conversation_type: str = Field(default="dm", example="dm")  # Could also be "group"


class Conversation(BaseModel):
    """
    Model for returning conversation data.
    """

    id: str = Field(..., alias="_id")
    participants: List[str]
    conversation_type: str
    created_at: Optional[datetime] = None
    history: Optional[List[dict]] = Field(default_factory=list)

    class Config:
        from_attributes = True
        populate_by_field_name = True


# ---------------------------------
# AI Models
# ---------------------------------


class AI(BaseModel):
    """
    Model representing an AI agent.
    """

    id: str = Field(..., alias="_id")
    name: str = Field(..., example="FriendlyBot")
    age: Optional[int] = Field(None, example=2)
    details: Optional[str] = Field(None, example="A friendly AI assistant.")
    personality: Optional[str] = Field("friendly", example="friendly")

    class Config:
        from_attributes = True
        populate_by_field_name = True


# ---------------------------------
# Additional Models (if needed)
# ---------------------------------


# You can define other models here, for example, models for login, or for updating profiles.
