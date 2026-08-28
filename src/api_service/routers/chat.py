from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from src.agent.runner import run_agent
from src.database.base_engine import get_db
from src.voice_call.runtime import get_checkpointer
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "dev-session"
    caller_phone_number: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str


@router.post(
    "",
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