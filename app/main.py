# app/main.py (snippet)
from fastapi import FastAPI
from app.routes.user import router as user_router
from app.routes.chat import router as chat_router
from app.routes.conversation import router as conversation_router

app = FastAPI(title="AI Chat Backend")

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(conversation_router, prefix="/conversation", tags=["Conversation"])


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Chat Backend"}
