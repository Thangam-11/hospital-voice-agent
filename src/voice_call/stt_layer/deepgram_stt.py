"""
Deepgram streaming speech-to-text client.

Uses Deepgram's raw WebSocket API directly (not the SDK) so the interface
stays stable regardless of SDK version churn, and so it's trivial to mock
in tests. Twilio Media Streams sends audio as 8kHz mulaw — Deepgram accepts
that encoding natively, so no audio conversion is needed on the way in.

NOTE: verify query params against Deepgram's current docs before relying on
this in production — streaming API parameters do change between versions.
"""

import asyncio
import json
from typing import AsyncIterator, Callable

import websockets

DEEPGRAM_WS_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=mulaw&sample_rate=8000&channels=1"
    "&punctuate=true&interim_results=true&endpointing=300&language=en-IN"
)


class DeepgramSTTSession:
    """One STT session per call. Feed it audio chunks; it yields
    (transcript, is_final) tuples as Deepgram produces them."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._ws = None

    async def connect(self):
        self._ws = await websockets.connect(
            DEEPGRAM_WS_URL,
            additional_headers={"Authorization": f"Token {self.api_key}"},
        )

    async def send_audio(self, mulaw_bytes: bytes):
        """Forward one chunk of raw mulaw audio from Twilio straight through."""
        if self._ws is None:
            raise RuntimeError("DeepgramSTTSession.connect() must be called first")
        await self._ws.send(mulaw_bytes)

    async def transcripts(self) -> AsyncIterator[tuple[str, bool]]:
        """Async generator yielding (transcript_text, is_final) as results
        arrive. Caller runs this as a background task alongside send_audio."""
        if self._ws is None:
            raise RuntimeError("DeepgramSTTSession.connect() must be called first")

        async for raw_message in self._ws:
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            if data.get("type") != "Results":
                continue

            alternatives = data.get("channel", {}).get("alternatives", [])
            if not alternatives:
                continue

            transcript = alternatives[0].get("transcript", "")
            if not transcript:
                continue

            is_final = bool(data.get("is_final") or data.get("speech_final"))
            yield transcript, is_final

    async def close(self):
        if self._ws is not None:
            await self._ws.close()