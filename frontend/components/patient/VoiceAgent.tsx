"use client";

import { Mic } from "lucide-react";
import { useState } from "react";

import VoiceAssistant from "@/components/voice/VoiceAssistant";

export function VoiceAgent() {
  const [showAssistant, setShowAssistant] = useState(false);
  const serverUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL || "";
  const token = "";

  return (
    <>
      {!showAssistant && (
        <div className="text-center">
          <div className="relative mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[#0D9488]">
            <Mic className="h-6 w-6 text-white" />
            <span className="absolute -right-0.5 -top-0.5 h-3.5 w-3.5 rounded-full border-2 border-white bg-[#2DD4BF]" />
          </div>
          <h1 className="mt-5 text-xl font-semibold text-slate-900">
            Talk to our AI Assistant
          </h1>
          <p className="mt-1.5 max-w-sm text-sm text-slate-500">
            Ask about appointments, doctors, or hospital information.
          </p>
          <button
            type="button"
            onClick={() => setShowAssistant(true)}
            className="mt-5 rounded-full bg-[#0D9488] px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#0F766E]"
          >
            Start Voice Agent
          </button>
        </div>
      )}

      {showAssistant && (
        <VoiceAssistant
          token={token}
          serverUrl={serverUrl}
          onClose={() => setShowAssistant(false)}
        />
      )}
    </>
  );
}
