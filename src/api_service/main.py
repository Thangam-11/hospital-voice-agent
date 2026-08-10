"""
FastAPI entrypoint. Run with:
    uvicorn src.main:app --reload
"""

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_engine import get_db
from src.agent.orchestrator import AgentOrchestrator
from src.configure.settings import get_settings
from src.api_service.routers.appointment import router as appointment_router

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(appointment_router)

# One orchestrator per call in a real deployment (keyed by call_sid, with
# conversation history persisted/restored per call). For local text-testing
# via /chat, a single in-memory instance is enough to iterate on the agent
# before wiring up Twilio.
_dev_orchestrator: AgentOrchestrator | None = None


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, session: AsyncSession = Depends(get_db)):
    """
    Text-based endpoint for testing the agent's tool-calling behavior
    without voice in the loop yet. Same orchestrator that will eventually
    sit behind the Twilio webhook.
    """
    global _dev_orchestrator
    if _dev_orchestrator is None:
        _dev_orchestrator = AgentOrchestrator(session)

    reply = await _dev_orchestrator.handle_turn(payload.message)
    return ChatResponse(reply=reply)


# Twilio voice webhook — stub for now, filled in once the text-based agent
# (via /chat above) is behaving correctly. See roadmap step 5.
@app.post("/voice/webhook")
async def voice_webhook():
    return {"status": "not_implemented"}