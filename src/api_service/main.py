"""
FastAPI entrypoint.

Run with:

    uvicorn src.api_service.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.configure.settings import get_settings

from src.api_service.routers.appointment import (
    router as appointment_router,
)

from src.api_service.routers.patient import (
    router as patient_router,
)

from src.api_service.routers.doctor import (
    router as doctor_router,
)

from src.api_service.routers.dashboard import (
    router as dashboard_router,
)

from src.api_service.routers.voice import (
    router as voice_router,
)

from src.api_service.routers.activity_logs import (
    router as activity_logsrouter,
)

from src.api_service.routers.auth import (
    router as auth_router,
)

from src.api_service.routers.chat import (
    router as chat_router,
)


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
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router)

app.include_router(chat_router)

app.include_router(appointment_router)

app.include_router(patient_router)

app.include_router(doctor_router)

app.include_router(dashboard_router)

app.include_router(voice_router)

app.include_router(activity_logsrouter)


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
# Voice webhook
# ---------------------------------------------------------------------------

@app.post("/voice/webhook")
async def voice_webhook():
    return {
        "status": "not_implemented"
    }