# app/services/ai_group_service.py

import asyncio
from app.services.conversation_service import (
    get_conversation,
    update_conversation_history_record,
)
from app.services.ai_service import get_ai_response
from app.repositories.user_repository import get_user_by_id
from app.repositories.ai_repository import get_ai_by_id as get_ai_by_id_repo


async def get_participant_names(participants: list) -> list:
    """
    Given a list of participant IDs, return their display names.
    Try to fetch as a user first; if not found, try as an AI.
    """
    names = []
    for pid in participants:
        name = None
        # Try as user
        try:
            user = await get_user_by_id(pid)
            if user:
                name = user.get("username")
                print(name)
        except Exception:
            pass
        # Try as AI if not found
        if not name:
            try:
                ai = await get_ai_by_id_repo(pid)
                if ai:
                    name = ai.get("name")
            except Exception:
                pass
        names.append(name if name else pid)
        print(names)
    return names


async def automate_group_ai_response(conversation_id: str):
    """
    For a group chat conversation, automatically generate an AI response.
    The AI will be aware it is in a group chat, know the names of the participants,
    and also know which user sent the latest message.
    """
    print("Automating group AI response...")
    # Load conversation
    conversation = await get_conversation(conversation_id)
    if not conversation or conversation.get("conversation_type") != "group":
        return None  # Only process group conversations

    history = conversation.get("history", [])
    participants = conversation.get("participants", [])

    # Find the AI in the group chat (assume one AI per group)
    ai_id = None
    for pid in participants:
        ai = await get_ai_by_id_repo(pid)
        if ai:
            ai_id = pid
            break

    # Retrieve participant names
    names = await get_participant_names(participants)
    print("names", names)

    # Inject AI personality in group chat
    if ai_id:
        ai_details = await get_ai_by_id_repo(ai_id)
        ai_name = ai_details.get("name", "AI")
        ai_personality = ai_details.get("personality", "friendly")
        ai_description = ai_details.get("details", "An AI assistant.")

        group_prompt = (
            f"You are {ai_name}, an AI participant in this group chat. "
            f"Your personality is {ai_personality}. {ai_description} "
            f"Here are the participants: {', '.join(names)}. "
            f"Please respond appropriately in character."
        )
    else:
        group_prompt = f"This is a group chat with participants: {', '.join(names)}. Please respond appropriately."
        print(group_prompt)

    # Ensure the system prompt is added or updated
    if not any(msg.get("role") == "system" for msg in history):
        history.insert(0, {"role": "system", "content": group_prompt})
    else:
        for idx, msg in enumerate(history):
            if msg.get("role") == "system":
                history[idx] = {"role": "system", "content": group_prompt}
                break

    # Ensure the AI responds to the latest user message
    last_message = None
    last_user_sender = None
    for msg in reversed(history):
        if msg.get("role") == "user":
            last_message = msg.get("content", "").strip()
            last_user_sender = msg.get(
                "sender"
            )  # Expecting the sender field to be present
            break

    if not last_message or last_message == "":
        print("No valid user message found. Skipping AI response.")
        return  # No user message to respond to

    # Construct input prompt including sender's name if available
    if last_user_sender:
        ai_input = f"As {ai_name}, respond to this group chat message from {last_user_sender}: {last_message}"
    else:
        ai_input = f"As {ai_name}, respond to this group chat message: {last_message}"

    # Debug print
    print(f"Latest user message for AI: {last_message}")
    print(f"AI input prompt: {ai_input}")

    # Generate AI response
    try:
        ai_response = await get_ai_response(ai_input, history, model="gpt-4o-mini")
        print("Generated AI response:", ai_response)
    except Exception as e:
        raise Exception(f"Failed to generate group AI response: {e}")

    # Append the AI's response to the conversation history
    history.append({"role": "assistant", "content": ai_response})
    updated_conversation = await update_conversation_history_record(
        conversation_id, history
    )
    return updated_conversation
