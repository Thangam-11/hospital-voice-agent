"use client";

import { CalendarPlus, Mic, Phone, Send } from "lucide-react";
import { useState } from "react";

import { BookAppointmentModal } from "@/components/appointments/book-appointment-modal";
import VoiceAssistant from "@/components/voice/VoiceAssistant";
import { sendChatMessage } from "@/lib/api/chat";
import type { ChatMessage } from "@/lib/api/chat";

const TOLL_FREE_NUMBER =
  process.env.NEXT_PUBLIC_TOLL_FREE_NUMBER || "1-800-000-0000";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface VoiceTokenResponse {
  server_url: string;
  participant_token: string;
  room_name: string;
  participant_identity: string;
}

export default function VoiceAgentPage() {
  // ============================================================
  // VOICE STATE
  // ============================================================

  const [showAssistant, setShowAssistant] = useState(false);
  const [voiceToken, setVoiceToken] = useState("");
  const [voiceServerUrl, setVoiceServerUrl] = useState("");
  const [voiceLoading, setVoiceLoading] = useState(false);
  const [voiceError, setVoiceError] = useState("");

  // ============================================================
  // APPOINTMENT STATE
  // ============================================================

  const [showBooking, setShowBooking] = useState(false);

  // ============================================================
  // CHAT STATE
  // ============================================================

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [chatError, setChatError] = useState("");

  // ============================================================
  // START VOICE ASSISTANT
  // ============================================================

  async function startVoiceAssistant() {
    if (voiceLoading) return;

    setVoiceLoading(true);
    setVoiceError("");

    try {
      const roomName = `hospital-room-${Date.now()}`;
      const participantIdentity = `patient-${Date.now()}`;
      const participantName = "Hospital Patient";

      console.log("=================================");
      console.log("Starting voice assistant...");
      console.log("API URL:", API_URL);
      console.log("Room:", roomName);
      console.log("Participant:", participantIdentity);
      console.log("=================================");

      // ----------------------------------------------------------
      // Request LiveKit token from FastAPI
      // ----------------------------------------------------------

      const response = await fetch(`${API_URL}/voice/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          room_name: roomName,
          participant_identity: participantIdentity,
          participant_name: participantName,
        }),
      });

      console.log("Token API status:", response.status);

      // ----------------------------------------------------------
      // Handle API errors
      // ----------------------------------------------------------

      if (!response.ok) {
        let message = `Failed to generate voice token (${response.status})`;

        try {
          const errorData = await response.json();

          console.error("Token API error:", errorData);

          if (errorData?.detail) {
            message =
              typeof errorData.detail === "string"
                ? errorData.detail
                : JSON.stringify(errorData.detail);
          }
        } catch {
          // Ignore JSON parsing error
        }

        throw new Error(message);
      }

      // ----------------------------------------------------------
      // Read backend response
      // ----------------------------------------------------------

      const data: VoiceTokenResponse = await response.json();

      console.log("VOICE TOKEN RESPONSE:", {
        server_url: data.server_url,
        room_name: data.room_name,
        participant_identity: data.participant_identity,
        has_token: Boolean(data.participant_token),
      });

      // ----------------------------------------------------------
      // Validate participant token
      // ----------------------------------------------------------

      if (!data.participant_token) {
        throw new Error(
          "Backend did not return a LiveKit participant token.",
        );
      }

      // ----------------------------------------------------------
      // Validate LiveKit server URL
      // ----------------------------------------------------------

      if (!data.server_url) {
        throw new Error("LiveKit server URL is missing.");
      }

      // ----------------------------------------------------------
      // Save token and server URL
      // ----------------------------------------------------------

      setVoiceToken(data.participant_token);
      setVoiceServerUrl(data.server_url);

      // ----------------------------------------------------------
      // Open voice assistant
      // ----------------------------------------------------------

      setShowAssistant(true);

      console.log("VoiceAssistant opened.");
    } catch (error) {
      console.error("Voice assistant error:", error);

      setVoiceError(
        error instanceof Error
          ? error.message
          : "Failed to start voice assistant.",
      );
    } finally {
      setVoiceLoading(false);
    }
  }

  // ============================================================
  // CLOSE VOICE ASSISTANT
  // ============================================================

  function closeVoiceAssistant() {
    setShowAssistant(false);
    setVoiceToken("");
    setVoiceServerUrl("");
    setVoiceError("");
  }

  // ============================================================
  // CHAT
  // ============================================================

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();

    const text = input.trim();

    if (!text || sending) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text,
      },
    ]);

    setInput("");
    setSending(true);
    setChatError("");

    try {
      const reply = await sendChatMessage(text);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: reply,
        },
      ]);
    } catch (err) {
      setChatError(
        err instanceof Error
          ? err.message
          : "Failed to reach the AI assistant.",
      );
    } finally {
      setSending(false);
    }
  }

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      {/* ========================================================
          LEFT SIDE
      ======================================================== */}

      <div className="space-y-5 lg:col-span-1">
        {/* ======================================================
            LIVE VOICE CARD
        ====================================================== */}

        <div className="flex flex-col items-center rounded-xl border border-slate-200 bg-white px-6 py-10 text-center">
          <div className="relative flex h-14 w-14 items-center justify-center rounded-full bg-[#0D9488]">
            <Mic className="h-6 w-6 text-white" />

            <span className="absolute -right-0.5 -top-0.5 h-3.5 w-3.5 rounded-full border-2 border-white bg-[#2DD4BF]" />
          </div>

          <h2 className="mt-4 text-base font-semibold text-slate-900">
            Live Voice Call
          </h2>

          <p className="mt-1.5 text-sm text-slate-500">
            Start a real-time voice conversation with the assistant.
          </p>

          {/* START VOICE BUTTON */}

          <button
            type="button"
            onClick={startVoiceAssistant}
            disabled={voiceLoading}
            className="mt-5 rounded-full bg-[#0D9488] px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#0F766E] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {voiceLoading ? "Connecting..." : "Start Voice Agent"}
          </button>

          {/* VOICE ERROR */}

          {voiceError && (
            <div className="mt-3 w-full rounded-lg bg-red-50 px-3 py-2 text-left text-xs text-red-600">
              {voiceError}
            </div>
          )}
        </div>

        {/* ======================================================
            TOLL FREE
        ====================================================== */}

        <div className="rounded-xl border border-slate-200 bg-white px-6 py-6">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
            <Phone className="h-4 w-4 text-[#0D9488]" />

            <span>Call our toll-free line</span>
          </div>

          <a
            href={`tel:${TOLL_FREE_NUMBER.replace(/[^0-9+]/g, "")}`}
            className="mt-2 block text-2xl font-semibold tracking-tight text-[#0D9488] hover:underline"
          >
            {TOLL_FREE_NUMBER}
          </a>

          <p className="mt-1.5 text-xs text-slate-400">
            Available 24/7 — talk to the AI assistant to book,
            reschedule, or cancel an appointment over the phone.
          </p>
        </div>
      </div>

      {/* ========================================================
          RIGHT SIDE — CHAT
      ======================================================== */}

      <div className="flex flex-col rounded-xl border border-slate-200 bg-white lg:col-span-2">
        {/* CHAT HEADER */}

        <div className="border-b border-slate-200 px-5 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Chat with the AI Assistant
              </h2>

              <p className="mt-0.5 text-xs text-slate-400">
                Prefer typing? Ask about appointments, doctors, or
                departments.
              </p>
            </div>

            {/* BOOK APPOINTMENT */}

            <button
              type="button"
              onClick={() => setShowBooking(true)}
              className="flex shrink-0 items-center gap-1.5 rounded-lg bg-[#0D9488]/10 px-3 py-2 text-xs font-semibold text-[#0D9488] transition-colors hover:bg-[#0D9488]/15"
            >
              <CalendarPlus className="h-3.5 w-3.5" />

              Book Appointment
            </button>
          </div>
        </div>

        {/* CHAT MESSAGES */}

        <div
          className="flex-1 space-y-3 overflow-y-auto px-5 py-4"
          style={{
            minHeight: 360,
            maxHeight: 480,
          }}
        >
          {messages.length === 0 ? (
            <p className="pt-16 text-center text-sm text-slate-400">
              Say hello to get started.
            </p>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[75%] rounded-lg px-3.5 py-2 text-sm ${
                    message.role === "user"
                      ? "bg-[#0D9488] text-white"
                      : "bg-slate-100 text-slate-700"
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))
          )}

          {/* TYPING */}

          {sending && (
            <div className="flex justify-start">
              <div className="rounded-lg bg-slate-100 px-3.5 py-2 text-sm text-slate-400">
                Typing…
              </div>
            </div>
          )}
        </div>

        {/* CHAT ERROR */}

        {chatError && (
          <p className="px-5 pb-2 text-xs text-red-600">
            {chatError}
          </p>
        )}

        {/* CHAT INPUT */}

        <form
          onSubmit={handleSend}
          className="flex items-center gap-2 border-t border-slate-200 px-4 py-3"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 rounded-lg border border-slate-200 px-3.5 py-2 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
          />

          <button
            type="submit"
            disabled={sending || !input.trim()}
            className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#0D9488] text-white transition-colors hover:bg-[#0F766E] disabled:opacity-50"
            aria-label="Send"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>

      {/* ========================================================
          VOICE ASSISTANT
      ======================================================== */}

      {showAssistant && voiceToken && voiceServerUrl && (
        <VoiceAssistant
          token={voiceToken}
          serverUrl={voiceServerUrl}
          onClose={closeVoiceAssistant}
        />
      )}

      {/* ========================================================
          BOOK APPOINTMENT MODAL
      ======================================================== */}

      {showBooking && (
        <BookAppointmentModal
          onClose={() => setShowBooking(false)}
          onBooked={() => {
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content:
                  "Your appointment has been booked successfully.",
              },
            ]);
          }}
        />
      )}
    </div>
  );
}