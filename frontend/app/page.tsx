"use client";

import { useState } from "react";
import VoiceAssistant from "@/components/voice/VoiceAssistant";

export default function Home() {
  const [showAssistant, setShowAssistant] = useState(false);

  const serverUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL || "";
  const token = "";

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="flex min-h-screen flex-col items-center justify-center px-6">
        <div className="w-full max-w-lg rounded-2xl bg-white p-8 text-center shadow-lg">
          <h1 className="text-3xl font-bold text-gray-900">
            Hospital Voice Assistant
          </h1>

          <p className="mt-3 text-gray-600">
            Talk to our AI assistant to book appointments and get hospital
            information.
          </p>

          <button
            type="button"
            onClick={() => setShowAssistant(true)}
            className="mt-8 rounded-full bg-blue-600 px-8 py-3 font-semibold text-white transition hover:bg-blue-700"
          >
            Start Voice Assistant
          </button>
        </div>
      </div>

      {showAssistant && (
        <VoiceAssistant
          token={token}
          serverUrl={serverUrl}
          onClose={() => setShowAssistant(false)}
        />
      )}
    </main>
  );
}
