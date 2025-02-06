# app/routes/ai.py

from fastapi import APIRouter, HTTPException, status
from app.models import AI
from app.repositories.ai_repository import (
    create_ai,
    get_ai_by_id,
    list_all_ais,
    update_ai,
    delete_ai,
)
from typing import List

router = APIRouter()


@router.post("/", response_model=AI, status_code=status.HTTP_201_CREATED)
async def create_ai_endpoint(ai: AI):
    """
    Create a new AI agent.
    """
    return await create_ai(ai.model_dump())


@router.get("/{ai_id}", response_model=AI)
async def get_ai_endpoint(ai_id: str):
    """
    Retrieve an AI agent by its ID.
    """
    ai_instance = await get_ai_by_id(ai_id)
    if not ai_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AI not found"
        )
    return ai_instance


@router.get("/", response_model=List[AI])
async def list_ais_endpoint():
    """
    List all AI agents.
    """
    return await list_all_ais()


@router.put("/{ai_id}", response_model=AI)
async def update_ai_endpoint(ai_id: str, ai: AI):
    """
    Update an existing AI agent.
    """
    return await update_ai(ai_id, ai.model_dump(exclude_unset=True))


@router.delete("/{ai_id}")
async def delete_ai_endpoint(ai_id: str):
    """
    Delete an AI agent.
    """
    return await delete_ai(ai_id)
