"""
FastAPI entrypoint. Run with:
    uvicorn src.main:app --reload
"""

from typing import Optional

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage

from src.database.base_engine import get_db
from src.agent.agent_core import build_agent
from src.configure.settings import get_settings
from src.api_service.routers.appointment import router as appointment_router
from src.service.appointment_service import AppointmentService
from src.service.patient_service import PatientService

from src.api_service.routers.patient import router as patient_router
from langgraph.errors import GraphRecursionError
from langgraph.checkpoint.memory import MemorySaver
# Swap for a persistent checkpointer in production, e.g.:
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# ... existing imports ...

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(appointment_router)
app.include_router(patient_router)

# One checkpointer for the app's lifetime. Conversation memory across
# turns of the same conversation_id depends on THIS instance being
# reused — a fresh MemorySaver per request would silently make every
# turn forget everything before it, even with a matching thread_id.
_checkpointer = MemorySaver()


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "dev-session"


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, session: AsyncSession = Depends(get_db)):
    appointment_service = AppointmentService(session)
    patient_service = PatientService(session)
    agent = build_agent(appointment_service, patient_service, _checkpointer)

    config = {
        "configurable": {"thread_id": payload.conversation_id},
        "recursion_limit": 15,
    }

    try:
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=payload.message)]},
            config=config,
        )
    except GraphRecursionError:
        return ChatResponse(
            reply="Something went wrong on my end — let me connect you with a staff member."
        )

    last_message = result["messages"][-1]
    return ChatResponse(reply=last_message.content)


@app.post("/voice/webhook")
async def voice_webhook():
    return {"status": "not_implemented"}