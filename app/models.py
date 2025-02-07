"""
Module: app.models

This module defines the Pydantic models used throughout the application.
It includes models for user operations, chat messages, conversations, and AI agents.
These models are used for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ---------------------------------
# User Models
# ---------------------------------


class UserCreate(BaseModel):
    """
    Model for user sign-up requests.

    Attributes:
        username (str): The desired username for the new user.
                        Example: "john_doe"
        password (str): The password for the new user. Must be at least 6 characters long.
                        Example: "securepass123"
    """

    username: str = Field(
        ..., example="john_doe", description="The desired username for the new user."
    )
    password: str = Field(
        ...,
        min_length=6,
        example="securepass123",
        description="The password for the new user (min 6 characters).",
    )


class UserResponse(BaseModel):
    """
    Model for returning user data.

    Attributes:
        id (str): The unique identifier of the user (as a string).
                  This field is populated from the database's '_id' field.
                  Example: "605c72f7e3a1d72f1c8f9a0b"
        username (str): The username of the user.
                        Example: "john_doe"
        created_at (Optional[datetime]): The UTC timestamp when the user was created.
                                          Example: "2024-11-20T18:33:13.953000"
    """

    id: str = Field(
        ...,
        alias="_id",
        description="The unique identifier of the user (string representation).",
    )
    username: str = Field(..., description="The username of the user.")
    created_at: Optional[datetime] = Field(
        None, description="UTC timestamp when the user was created."
    )

    class Config:
        from_attributes = True
        populate_by_name = True


# ---------------------------------
# Chat Message Models
# ---------------------------------


class Message(BaseModel):
    """
    Model for chat messages.

    Attributes:
        sender (str): The identifier or name of the sender.
                      Example: "john_doe"
        content (str): The textual content of the message.
                       Example: "Hello, how are you?"
        timestamp (Optional[datetime]): The UTC time when the message was created.
                                          This is automatically set to the current UTC time.
    """

    sender: str = Field(
        ..., example="john_doe", description="The identifier or username of the sender."
    )
    content: str = Field(
        ...,
        example="Hello, how are you?",
        description="The textual content of the message.",
    )
    timestamp: Optional[datetime] = Field(
        default_factory=lambda: datetime.utcnow(),
        description="The UTC timestamp when the message was created.",
    )

    class Config:
        from_attributes = True


# ---------------------------------
# Conversation Models
# ---------------------------------


class ConversationCreate(BaseModel):
    """
    Model for creating a new conversation.

    Attributes:
        participants (List[str]): A list of user and/or AI IDs participating in the conversation.
                                    Example: ["user_id_1", "user_id_2"]
        conversation_type (str): The type of conversation. This can be "dm" for direct messages or "group" for group chats.
                                 Example: "dm"
    """

    participants: List[str] = Field(
        ...,
        example=["user_id_1", "user_id_2"],
        description="List of participant IDs (users or AIs).",
    )
    conversation_type: str = Field(
        default="dm",
        example="dm",
        description="The type of conversation ('dm' or 'group').",
    )


class Conversation(BaseModel):
    """
    Model for returning conversation data.

    Attributes:
        id (str): The unique identifier of the conversation (as a string).
                  This field is populated from the database's '_id' field.
        participants (List[str]): A list of participant IDs in the conversation.
        conversation_type (str): The type of conversation ("dm" or "group").
        created_at (Optional[datetime]): The UTC timestamp when the conversation was created.
        history (Optional[List[dict]]): A list of message objects (each as a dictionary) representing the conversation history.
                                        Each message should include at least the fields "role" and "content".
    """

    id: str = Field(
        ...,
        alias="_id",
        description="The unique identifier of the conversation (string representation).",
    )
    participants: List[str] = Field(
        ..., description="List of participant IDs in the conversation."
    )
    conversation_type: str = Field(
        ..., description="The type of conversation (e.g., 'dm' or 'group')."
    )
    created_at: Optional[datetime] = Field(
        None, description="UTC timestamp when the conversation was created."
    )
    history: Optional[List[dict]] = Field(
        default_factory=list,
        description="List of messages (each as a dictionary) in the conversation history.",
    )

    class Config:
        from_attributes = True
        populate_by_field_name = True


# ---------------------------------
# AI Models
# ---------------------------------


class AI(BaseModel):
    """
    Model representing an AI agent.

    Attributes:
        id (str): The unique identifier of the AI agent (as a string).
                  This field is populated from the database's '_id' field.
                  Example: "605c73f8e3a1d72f1c8f9a1c"
        name (str): The display name of the AI agent.
                    Example: "FriendlyBot"
        age (Optional[int]): The age of the AI agent (if applicable).
                             Example: 2
        details (Optional[str]): A description of the AI agent, including its capabilities and role.
                                 Example: "A friendly AI assistant."
        personality (Optional[str]): The personality trait of the AI agent.
                                     Example: "friendly"
    """

    id: str = Field(
        ...,
        alias="_id",
        description="The unique identifier of the AI agent (string representation).",
    )
    name: str = Field(
        ..., example="FriendlyBot", description="The display name of the AI agent."
    )
    age: Optional[int] = Field(
        None, example=2, description="The age of the AI agent, if applicable."
    )
    details: Optional[str] = Field(
        None,
        example="A friendly AI assistant.",
        description="A description of the AI agent.",
    )
    personality: Optional[str] = Field(
        "friendly",
        example="friendly",
        description="The personality trait of the AI agent.",
    )

    class Config:
        from_attributes = True
        populate_by_field_name = True


# ---------------------------------
# Additional Models (if needed)
# ---------------------------------

# Additional models for other functionalities (e.g., login, profile update) can be defined here.
