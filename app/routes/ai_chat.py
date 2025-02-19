# app/routes/ai_chat.py

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.repositories.ai_repository import get_ai_by_id
from app.services.ai.ai_service import get_ai_response, master_ai
from app.services.ai.ai_chunking_service import chunk_messages
from app.services.conversation_service import (
    create_new_conversation,
    get_conversation,
    update_conversation_history_record,
)
from app.services.user_service import get_user
from app.utils.auth import decode_access_token
import logging

# import our Celery task
from app.tasks import deliver_chunks_task

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
    conversation_history: List[dict]


@router.post("/{ai_id}", response_model=AIChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_ai(
    ai_id: str,
    request: AIChatRequest,
    token: str = Depends(oauth2_scheme),
):
    """
    Chat with a specific AI agent.

    Now using Celery for scheduling chunked responses (ready for production scale).
    """
    # 1. Verify JWT
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user id found.",
            )

        user_data = await get_user({"id": user_id})
        print(user_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token."
        )

    # 2. Retrieve AI details
    ai_details = await get_ai_by_id(ai_id)
    if not ai_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI not found."
        )

    # 3. Prepare or retrieve conversation
    if request.chat_id:
        conversation = await get_conversation(request.chat_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found."
            )
        chat_id = conversation.get("id") or conversation.get("_id")
        conversation_history = conversation.get("history", [])

        # If there's an ongoing chunk delivery, mark it interrupted
        conversation["interrupted"] = True
        await update_conversation_history_record(
            chat_id, conversation_history, interrupted=True
        )
    else:
        # Create new conversation doc
        conversation_data = {
            "participants": [user_id, ai_details.get("id") or ai_details.get("_id")],
            "conversation_type": "ai",
            "created_at": datetime.utcnow(),
            "history": [],
        }
        conversation = await create_new_conversation(
            conversation_data, skip_participant_check=True
        )
        chat_id = conversation.get("id") or conversation.get("_id")
        conversation_history = []

    # 4. Ensure system message is present
    logger.info("Ensuring system message is present")
    system_message = (
        f"You are {ai_details.get('name', 'an AI')} with personality "
        f"{ai_details.get('personality', 'friendly')}. {ai_details.get('details', '')}"
    )
    if not any(msg.get("role") == "system" for msg in conversation_history):
        conversation_history.insert(0, {"role": "system", "content": system_message})

    # 5. Append user's message
    conversation_history.append({"role": "user", "content": request.message})

    logger.info("Getting master AI's decision")
    # 6. Get the master AI's decision
    try:
        master_ai_response = await master_ai(
            request.message, user_data, ai_details, conversation_history
        )
        print(master_ai_response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    # 7. Determine scheduling plan using the "scheduling AI"
    try:
        chunks = await chunk_messages(
            conversation_history,
            user_data,
            ai_details,
            request.message,
            master_ai_response,
        )
        print("Scheduling plan:", chunks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to chunk response: {e}",
        )

    # 8. Update the conversation record so it's not interrupted
    updated_conversation = await update_conversation_history_record(
        chat_id, conversation_history, interrupted=False
    )

    # 9. Dispatch the Celery task with the scheduling plan
    # We pass the conversation ID and the scheduling plan so the worker can fetch
    # conversation data from DB (or we could pass them directly)
    deliver_chunks_task.delay(chat_id, chunks)

    # 10. Return an immediate response so the user sees something now
    return AIChatResponse(
        chat_id=chat_id,
        conversation_history=updated_conversation.get("history", conversation_history),
    )
