# app/routes/ai_chat.py

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.repositories.ai_repository import get_ai_by_id
from app.services.ai_service import get_ai_response
from app.services.conversation_service import (
    create_new_conversation,
    get_conversation,
    update_conversation_history_record,
)
from app.utils.auth import decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


class AIChatRequest(BaseModel):
    """
    Request model for chatting with an AI.
    Only includes the user's new message and an optional chat_id.
    """

    message: str = Field(..., example="Hello, can you help me?")
    chat_id: Optional[str] = Field(None, example="62e5a...")


class AIChatResponse(BaseModel):
    """
    Response model for AI chat.
    """

    chat_id: str
    response: str
    conversation_history: List[dict]


@router.post("/{ai_id}", response_model=AIChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_ai(
    ai_id: str,  # The ID of the AI agent to chat with
    request: AIChatRequest,
    token: str = Depends(oauth2_scheme),
):
    """
    Chat with a specific AI agent.

    If a chat_id is provided, the conversation history is loaded from the database.
    If not, a new conversation is created between the user and the AI.

    Steps:
      1. Verify the JWT token.
      2. Retrieve the AI agent details.
      3. Load the existing conversation if chat_id is provided, otherwise create a new conversation.
         For AI conversations, skip the participant check since the AI is stored in a separate collection.
      4. Ensure the conversation history contains the system prompt (constructed from the AI's details).
      5. Append the user's new message to the conversation history.
      6. Call the AI service to generate a response.
      7. Append the assistant's response to the conversation history and update the conversation record.
      8. Return the chat_id, AI's response, and the updated conversation history.
    """
    # Verify JWT token
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user id found.",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token."
        )

    # Retrieve AI agent details
    ai_details = await get_ai_by_id(ai_id)
    if not ai_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI not found."
        )

    # Construct a system prompt from the AI's details.
    system_message = (
        f"You are {ai_details.get('name', 'an AI')} with personality "
        f"{ai_details.get('personality', 'friendly')}. {ai_details.get('details', '')}"
    )

    # Determine conversation history and chat_id
    if request.chat_id:
        # Load existing conversation from the database
        conversation = await get_conversation(request.chat_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found."
            )
        # Extract chat_id from either "id" or "_id"
        chat_id = conversation.get("id") or conversation.get("_id")
        conversation_history = conversation.get("history", [])
    else:
        # Create a new conversation record
        conversation_data = {
            "participants": [user_id, ai_details.get("id") or ai_details.get("_id")],
            "conversation_type": "ai",
            "created_at": datetime.utcnow(),
            "history": [],  # Start with an empty history
        }
        # Pass skip_participant_check=True because the AI is not in the users collection.
        conversation = await create_new_conversation(
            conversation_data, skip_participant_check=True
        )
        # Extract chat_id from either "id" or "_id"
        chat_id = conversation.get("id") or conversation.get("_id")
        conversation_history = []

    # Ensure the system message is present in the conversation history
    if not any(msg.get("role") == "system" for msg in conversation_history):
        conversation_history.insert(0, {"role": "system", "content": system_message})

    # Append the user's new message
    conversation_history.append({"role": "user", "content": request.message})

    # Generate AI response using the conversation history.
    try:
        ai_response = await get_ai_response(
            request.message, conversation_history, model="gpt-4o-mini"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    # Append the AI's response to the conversation history if it's not already added.
    if not any(
        msg.get("role") == "assistant" and msg.get("content") == ai_response
        for msg in conversation_history
    ):
        conversation_history.append({"role": "assistant", "content": ai_response})

    # Update the conversation record in the database with the new history.
    updated_conversation = await update_conversation_history_record(
        chat_id, conversation_history
    )

    # Return the chat_id, AI's response, and the updated conversation history.
    return AIChatResponse(
        chat_id=chat_id,
        response=ai_response,
        conversation_history=updated_conversation.get("history", conversation_history),
    )
