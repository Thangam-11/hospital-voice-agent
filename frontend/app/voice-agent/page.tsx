"use client";

import { Mic } from "lucide-react";

import VoiceAssistant from "@/components/voice/voiceassistant";
import { useVoiceCall } from "@/components/voice/usevoicecall";

export default function VoiceAgentPage() {
  const {
    isOpen,
    token,
    serverUrl,
    loading,
    error,
    startCall,
    endCall,
  } = useVoiceCall("Hospital Patient");

  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center px-6 py-16 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
        <Mic className="h-7 w-7 text-primary" />
      </div>

      <h1 className="mt-6 text-2xl font-semibold tracking-tight">
        Talk to the Voice Assistant
      </h1>

      <p className="mt-2 max-w-md text-sm text-muted-foreground">
        Book, cancel, or check an appointment by speaking naturally.
        The assistant will ask for your name and date of birth to
        verify your identity before making any changes.
      </p>

      {error && (
        <div className="mt-4 w-full max-w-sm rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <button
        onClick={startCall}
        disabled={loading}
        className="mt-8 inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-medium text-primary-foreground shadow-sm hover:bg-primary/90 disabled:opacity-50"
      >
        <Mic className="h-4 w-4" />
        {loading ? "Connecting…" : "Start Voice Call"}
      </button>

      {isOpen && token && serverUrl && (
        <VoiceAssistant
          token={token}
          serverUrl={serverUrl}
          onClose={endCall}
        />
      )}
    </div>
  );
}