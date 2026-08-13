"""
FastAPI entrypoint.

Run with:

    uvicorn src.main:app --reload
"""

from typing import Optional

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_engine import get_db
from src.configure.settings import get_settings

from src.api_service.routers.appointment import (
    router as appointment_router,
)

from src.api_service.routers.patient import (
    router as patient_router,
)
from src.api_service.routers.voice import router as voice_router
from src.agent.runner import run_agent
from src.voice_call.runtime import get_checkpointer


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

settings = get_settings()


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(appointment_router)
app.include_router(patient_router)
app.include_router(voice_router)

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


# ---------------------------------------------------------------------------
# Chat schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "dev-session"
    caller_phone_number: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    payload: ChatRequest,
    session: AsyncSession = Depends(get_db),
):

    checkpointer = await get_checkpointer()

    reply = await run_agent(
        session=session,
        checkpointer=checkpointer,
        call_sid=payload.conversation_id,
        patient_utterance=payload.message,
        caller_phone_number=payload.caller_phone_number,
    )

    return ChatResponse(
        reply=reply,
    )


# ---------------------------------------------------------------------------
# Voice webhook
# ---------------------------------------------------------------------------

@app.post("/voice/webhook")
async def voice_webhook():

    return {
        "status": "not_implemented"
    }