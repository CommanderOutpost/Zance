# app/routes/chat.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.chat_service import send_message, fetch_conversation_history
from app.models import Message
from typing import List, Dict
import asyncio
import json

# For JWT decoding and conversation authorization.
from app.utils.auth import decode_access_token
from app.services.conversation_service import (
    get_conversation,
    update_conversation_history_record,
)

# For Redis Pub/Sub.
from app.services.redis_pubsub import publish_message, subscribe_to_channel

router = APIRouter()

# In-memory store for local WebSocket connections per conversation.
# (This is only for local instance routing; message distribution is handled by Redis.)
local_connections: Dict[str, List[WebSocket]] = {}


@router.get("/conversation/{conversation_id}")
async def get_conversation_endpoint(conversation_id: str):
    messages = await fetch_conversation_history(conversation_id)
    return {"conversation_id": conversation_id, "messages": messages}


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """
    Secure WebSocket endpoint using JWT authentication & Redis Pub/Sub for distributed messaging.
    Clients must provide their token as a query parameter (e.g., ?token=YOUR_JWT).
    """
    # Extract token from query parameters.
    token = websocket.query_params.get("token")
    # print("Token received:", token)
    if not token:
        await websocket.close(code=1008)
        return

    # Decode token to get user info.
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        # print("Decoded payload:", payload)
        if not user_id:
            await websocket.close(code=1008)
            return
    except Exception as e:
        print("Error decoding token:", e)
        await websocket.close(code=1008)
        return

    # print("hello")

    # Authorization: check if user is a participant in the conversation.
    try:
        conversation = await get_conversation(conversation_id)
        print("Conversation data:", conversation)
        if not conversation:
            print("Conversation not found.")
            await websocket.close(code=1008)
            return
    except Exception as e:
        print("Error fetching conversation:", e)
        await websocket.close(code=1008)
        return

    if user_id not in conversation.get("participants", []):
        print("User not authorized for conversation.")
        await websocket.close(code=1008)
        return

    # Accept the WebSocket connection.
    await websocket.accept()

    # Add this websocket connection to the local store.
    if conversation_id not in local_connections:
        local_connections[conversation_id] = []
    local_connections[conversation_id].append(websocket)

    # -- User Presence: Mark the user as online for this conversation --
    # Optionally, add user_id to a Redis set for presence, e.g.:
    # await redis_client.sadd(f"conversation:{conversation_id}:presence", user_id)
    # Then, publish a presence update if needed.

    # Start a background task to subscribe to the Redis channel for this conversation.
    async def redis_listener():
        async for message in subscribe_to_channel(conversation_id):
            # Broadcast received message to local WebSocket connections.
            for conn in local_connections.get(conversation_id, []):
                try:
                    await conn.send_text(json.dumps(message))
                except Exception:
                    continue

    listener_task = asyncio.create_task(redis_listener())

    try:
        # Main WebSocket receive loop.
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
            except Exception:
                await websocket.send_text("Invalid message format. Please send JSON.")
                continue

            try:
                # Create a Message instance (automatically adds timestamp).
                message_obj = Message(**message_data)
            except Exception as e:
                await websocket.send_text(f"Error in message data: {e}")
                continue

            # Save the message in the database.
            saved_message = await send_message(conversation_id, message_obj)

            # Ensure the message is also added to the conversation history
            conversation = await get_conversation(conversation_id)
            if conversation:
                history = conversation.get("history", [])
                history.append(
                    {
                        "role": "user",
                        "sender": message_obj.sender,
                        "content": message_obj.content,
                    }
                )
                # Append user message
                await update_conversation_history_record(
                    conversation_id, history
                )  # Update DB

            # Publish the saved message to the Redis channel for distributed broadcasting.
            await publish_message(conversation_id, saved_message)

            # Trigger AI response after message is saved
            if conversation.get("conversation_type") == "group":
                if message_obj.sender:  # Ensures sender is a user
                    from app.services.ai.ai_group_service import automate_group_ai_response

                    asyncio.create_task(automate_group_ai_response(conversation_id))

            # For group chats, if the conversation type is "group" and the message is from a user,
            # trigger an automated AI response.

            conv = await get_conversation(conversation_id)
            if conv.get("conversation_type") == "group":
                if message_obj.sender:  # Ensure AI does not respond to itself
                    from app.services.ai.ai_group_service import automate_group_ai_response

                    # Prevent duplicate AI responses
                    if not any(
                        msg.get("role") == "assistant"
                        for msg in conversation.get("history", [])
                    ):
                        asyncio.create_task(automate_group_ai_response(conversation_id))

    except WebSocketDisconnect:
        # Remove the WebSocket from local connections on disconnect.
        if conversation_id in local_connections:
            local_connections[conversation_id].remove(websocket)
        # Optionally update presence here (e.g., remove from Redis set).
    finally:
        listener_task.cancel()
