"use client";

import { Mic } from "lucide-react";
import { useState } from "react";

import VoiceAssistant from "@/components/voice/VoiceAssistant";

export default function VoiceAgentPage() {
  const [showAssistant, setShowAssistant] = useState(false);
  const serverUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL || "";
  const token = "";

  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white px-6 py-20 text-center">
      <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-[#0D9488]">
        <Mic className="h-7 w-7 text-white" />
        <span className="absolute -right-0.5 -top-0.5 h-4 w-4 rounded-full border-2 border-white bg-[#2DD4BF]" />
      </div>

      <h2 className="mt-5 text-lg font-semibold text-slate-900">
        AI Voice Agent
      </h2>
      <p className="mt-2 max-w-sm text-sm text-slate-500">
        Start a live conversation with the assistant to book appointments,
        check doctor availability, or answer patient questions.
      </p>

      <button
        type="button"
        onClick={() => setShowAssistant(true)}
        className="mt-6 rounded-full bg-[#0D9488] px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0F766E]"
      >
        Start Voice Agent
      </button>

      {!serverUrl && (
        <p className="mt-3 text-xs text-red-600">
          NEXT_PUBLIC_LIVEKIT_URL is not set in .env.local.
        </p>
      )}

      {showAssistant && (
        <VoiceAssistant
          token={token}
          serverUrl={serverUrl}
          onClose={() => setShowAssistant(false)}
        />
      )}
    </div>
  );
}
