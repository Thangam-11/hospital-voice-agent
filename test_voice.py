import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("ELEVENLABS_VOICE_ID")

print("API key loaded:", bool(api_key))
print("Voice ID:", voice_id)

if not api_key:
    raise ValueError("ELEVENLABS_API_KEY is missing")

if not voice_id or voice_id == "your_voice_id_here":
    raise ValueError("ELEVENLABS_VOICE_ID is missing or still a placeholder")

client = ElevenLabs(api_key=api_key)

audio = client.text_to_speech.convert(
    voice_id=voice_id,
    text="Hello, this is a test of ElevenLabs text to speech.",
    model_id="eleven_multilingual_v2",
)

with open("elevenlabs_test.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("SUCCESS: elevenlabs_test.mp3 created")