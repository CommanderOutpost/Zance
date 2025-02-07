"""
AI Routes Module

Defines RESTful endpoints for managing AI agents.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from app.models import AI
from app.repositories.ai_repository import (
    create_ai,
    get_ai_by_id,
    list_all_ais,
    update_ai,
    delete_ai,
)

router = APIRouter()


@router.post("/", response_model=AI, status_code=status.HTTP_201_CREATED)
async def create_ai_endpoint(ai: AI) -> Dict[str, Any]:
    """
    Create a new AI agent.

    :param ai: An AI model instance.
    :return: The created AI agent document.
    """
    try:
        return await create_ai(ai.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AI agent: {e}",
        )


@router.get("/{ai_id}", response_model=AI)
async def get_ai_endpoint(ai_id: str) -> Dict[str, Any]:
    """
    Retrieve an AI agent by its ID.

    :param ai_id: The AI agent's ID.
    :return: The AI agent document.
    """
    ai_instance = await get_ai_by_id(ai_id)
    if not ai_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI not found"
        )
    return ai_instance


@router.get("/", response_model=List[AI])
async def list_ais_endpoint() -> List[Dict[str, Any]]:
    """
    List all AI agents.

    :return: A list of AI agent documents.
    """
    try:
        return await list_all_ais()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list AI agents: {e}",
        )


@router.put("/{ai_id}", response_model=AI)
async def update_ai_endpoint(ai_id: str, ai: AI) -> Dict[str, Any]:
    """
    Update an existing AI agent.

    :param ai_id: The ID of the AI agent to update.
    :param ai: An AI model instance with new data.
    :return: The updated AI agent document.
    """
    try:
        return await update_ai(ai_id, ai.model_dump(exclude_unset=True))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update AI agent: {e}",
        )


@router.delete("/{ai_id}")
async def delete_ai_endpoint(ai_id: str) -> Dict[str, Any]:
    """
    Delete an AI agent by its ID.

    :param ai_id: The ID of the AI agent to delete.
    :return: A dictionary confirming deletion.
    """
    try:
        return await delete_ai(ai_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete AI agent: {e}",
        )
