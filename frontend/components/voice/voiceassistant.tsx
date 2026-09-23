"use client";

import { X } from "lucide-react";

interface VoiceAssistantProps {
  token: string;
  serverUrl: string;
  onClose: () => void;
}

/**
 * Placeholder shell — wire this up to your existing LiveKit / voice
 * agent implementation. Kept minimal here since it wasn't part of
 * the dashboard bug being fixed.
 */
export default function VoiceAssistant({
  token,
  serverUrl,
  onClose,
}: VoiceAssistantProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 text-center shadow-xl">
        <div className="flex justify-end">
          <button onClick={onClose} aria-label="Close">
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        <p className="mt-2 text-sm text-gray-600">
          Connecting to voice agent…
        </p>
        {!serverUrl && (
          <p className="mt-2 text-xs text-red-600">
            NEXT_PUBLIC_LIVEKIT_URL is not set.
          </p>
        )}
      </div>
    </div>
  );
}
