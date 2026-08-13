"""
Twilio voice webhook.

Flow per call:
  1. Twilio POSTs to /voice/incoming when a call connects. We reply with
     TwiML that greets the caller and opens a <Gather> to listen for speech.
  2. Twilio transcribes speech itself (its built-in ASR) and POSTs the
     transcript to /voice/gather along with CallSid.
  3. We run that transcript through the SAME agent graph used by /chat,
     keyed by CallSid as the thread_id — so conversation state (patient_id,
     verification_attempts, etc.) persists correctly across turns within
     one call, exactly like it does across /chat turns today.
  4. We speak the agent's reply back via <Say>, then open another <Gather>
     to keep the conversation going, until the agent ends the call.

This uses Twilio's own speech-to-text and text-to-speech — good enough to
prove the full call flow works end to end. Swapping in Deepgram (streaming
STT) and ElevenLabs (higher-quality streaming TTS) later means replacing
this file's transport, not touching the agent/graph at all.
"""

from fastapi import APIRouter, Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather

from src.database.base_engine import AsyncSessionLocal
from src.service.appointment_service import AppointmentService
from src.service.patient_service import PatientService
from src.agent.agent_graph import build_agent
from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# Phrases that end the call — checked against the agent's reply text.
# Simple and good enough for now; a dedicated "end_call" tool (like
# respond_to_patient) would be a cleaner version of this later.
_END_CALL_MARKERS = ("goodbye", "have a great day", "have a good day")


async def _run_agent_turn(call_sid: str, user_text: str) -> str:
    """Runs one turn through the agent graph, keyed by call_sid so state
    persists across turns within the same call."""
    async with AsyncSessionLocal() as session:
        appointment_service = AppointmentService(session)
        patient_service = PatientService(session)
        agent = build_agent(appointment_service, patient_service)

        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_text}]},
            config={"configurable": {"thread_id": call_sid}},
        )

        last_message = result["messages"][-1]
        return getattr(last_message, "content", None) or str(last_message)


def _gather_response(reply_text: str) -> Response:
    """Builds TwiML: say the reply, then listen for the caller's next turn."""
    vr = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/voice/gather",
        method="POST",
        speech_timeout="auto",
        language="en-IN",
    )
    gather.say(reply_text)
    vr.append(gather)

    # If the caller says nothing at all, prompt once more before giving up.
    vr.say("Sorry, I didn't catch that. Please call back if you still need help.")
    vr.hangup()

    return Response(content=str(vr), media_type="application/xml")


@router.post("/incoming")
async def incoming_call(request: Request):
    """First webhook Twilio hits when a call connects."""
    form = await request.form()
    call_sid = form.get("CallSid", "unknown")
    caller = form.get("From", "unknown")
    logger.info("incoming_call: call_sid=%s from=%s", call_sid, caller)

    greeting = "Hello! Welcome to our hospital. How may I assist you today?"
    return _gather_response(greeting)


@router.post("/gather")
async def gather_speech(request: Request):
    """Twilio POSTs here with the transcribed speech after each <Gather>."""
    form = await request.form()
    call_sid = form.get("CallSid", "unknown")
    speech_result = form.get("SpeechResult", "")

    logger.info("gather_speech: call_sid=%s speech=%r", call_sid, speech_result)

    if not speech_result:
        return _gather_response("Sorry, could you repeat that?")

    try:
        reply_text = await _run_agent_turn(call_sid, speech_result)
    except Exception:
        logger.exception("gather_speech: agent turn failed for call_sid=%s", call_sid)
        reply_text = "Sorry, I'm having trouble right now. Let me transfer you to a team member."
        vr = VoiceResponse()
        vr.say(reply_text)
        vr.hangup()
        return Response(content=str(vr), media_type="application/xml")

    if any(marker in reply_text.lower() for marker in _END_CALL_MARKERS):
        vr = VoiceResponse()
        vr.say(reply_text)
        vr.hangup()
        logger.info("gather_speech: ending call_sid=%s", call_sid)
        return Response(content=str(vr), media_type="application/xml")

    return _gather_response(reply_text)