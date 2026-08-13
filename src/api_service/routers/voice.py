"""
Voice / LiveKit API routes.

This router generates LiveKit access tokens for the frontend.

IMPORTANT:
LIVEKIT_API_KEY and LIVEKIT_API_SECRET must NEVER be exposed
to the frontend.
"""

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from livekit import api

from src.configure.settings import get_settings
from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)

router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)

settings = get_settings()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class VoiceTokenRequest(BaseModel):
    """
    Request from the frontend when starting a voice session.
    """

    room_name: str | None = Field(
        default=None,
        description="LiveKit room name",
    )

    participant_identity: str | None = Field(
        default=None,
        description="Unique frontend participant identity",
    )

    participant_name: str | None = Field(
        default=None,
        description="Display name of the participant",
    )


class VoiceTokenResponse(BaseModel):
    """
    LiveKit connection information returned to the frontend.
    """

    server_url: str
    participant_token: str
    room_name: str
    participant_identity: str


# ---------------------------------------------------------------------------
# Create LiveKit token
# ---------------------------------------------------------------------------


@router.post(
    "/token",
    response_model=VoiceTokenResponse,
)
async def create_voice_token(
    payload: VoiceTokenRequest,
):
    """
    Generate a LiveKit access token.

    Flow:

        Frontend
            |
            | POST /voice/token
            v
        FastAPI
            |
            v
        LiveKit JWT
            |
            v
        Frontend connects to LiveKit
    """

    # ---------------------------------------------------------
    # Validate LiveKit configuration
    # ---------------------------------------------------------

    if not settings.livekit_api_key:
        logger.error("LIVEKIT_API_KEY is not configured")

        raise HTTPException(
            status_code=500,
            detail="LiveKit API key is not configured",
        )

    if not settings.livekit_api_secret:
        logger.error("LIVEKIT_API_SECRET is not configured")

        raise HTTPException(
            status_code=500,
            detail="LiveKit API secret is not configured",
        )

    if not settings.livekit_url:
        logger.error("LIVEKIT_URL is not configured")

        raise HTTPException(
            status_code=500,
            detail="LiveKit URL is not configured",
        )

    # ---------------------------------------------------------
    # Create room name
    # ---------------------------------------------------------

    room_name = payload.room_name or f"hospital-{uuid4().hex[:12]}"

    # ---------------------------------------------------------
    # Create participant identity
    # ---------------------------------------------------------

    participant_identity = (
        payload.participant_identity
        or f"patient-{uuid4().hex[:12]}"
    )

    participant_name = (
        payload.participant_name
        or "Patient"
    )

    logger.info(
        "Creating LiveKit token | room=%s | identity=%s",
        room_name,
        participant_identity,
    )

    # ---------------------------------------------------------
    # Create access token
    # ---------------------------------------------------------

    token = (
        api.AccessToken(
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        )
        .with_identity(participant_identity)
        .with_name(participant_name)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )

    logger.info(
        "LiveKit token created | room=%s | identity=%s",
        room_name,
        participant_identity,
    )

    return VoiceTokenResponse(
        server_url=settings.livekit_url,
        participant_token=token,
        room_name=room_name,
        participant_identity=participant_identity,
    )