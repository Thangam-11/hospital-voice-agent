"""
ElevenLabs streaming text-to-speech client.

Requests output_format=ulaw_8000 directly — that's exactly the format
Twilio Media Streams needs for playback, so no audio conversion/resampling
is required on the way out either.

NOTE: verify the message schema against ElevenLabs' current websocket docs
before relying on this in production.
"""

import base64
import json
from typing import AsyncIterator

import websockets

ELEVENLABS_WS_URL_TEMPLATE = (
    "wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input"
    "?model_id=eleven_turbo_v2_5&output_format=ulaw_8000"
)


class ElevenLabsTTSSession:
    """One TTS session per agent reply. Send text chunks, receive raw
    ulaw_8000 audio bytes ready to forward straight to Twilio."""

    def __init__(self, api_key: str, voice_id: str):
        self.api_key = api_key
        self.voice_id = voice_id
        self._ws = None

    async def connect(self):
        url = ELEVENLABS_WS_URL_TEMPLATE.format(voice_id=self.voice_id)
        self._ws = await websockets.connect(url)
        # Initial handshake message: auth + voice settings, empty text to open the stream.
        await self._ws.send(json.dumps({
            "text": " ",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
            "xi_api_key": self.api_key,
        }))

    async def speak(self, text: str) -> AsyncIterator[bytes]:
        """Send text and yield raw audio bytes as they stream back."""
        if self._ws is None:
            raise RuntimeError("ElevenLabsTTSSession.connect() must be called first")

        await self._ws.send(json.dumps({"text": text}))
        # Empty text signals "flush and finish" for this utterance.
        await self._ws.send(json.dumps({"text": ""}))

        async for raw_message in self._ws:
            data = json.loads(raw_message)
            audio_b64 = data.get("audio")
            if audio_b64:
                yield base64.b64decode(audio_b64)
            if data.get("isFinal"):
                break

    async def close(self):
        if self._ws is not None:
            await self._ws.close()