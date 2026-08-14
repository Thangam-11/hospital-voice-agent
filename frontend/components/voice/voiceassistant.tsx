"use client";

import {
  ControlBar,
  LiveKitRoom,
  RoomAudioRenderer,
} from "@livekit/components-react";

import "@livekit/components-styles";

interface VoiceAssistantProps {
  token: string;
  serverUrl: string;
  onDisconnected: () => void;
}

export default function VoiceAssistant({
  token,
  serverUrl,
  onDisconnected,
}: VoiceAssistantProps) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg overflow-hidden rounded-2xl bg-white shadow-xl">

        {/* Header */}
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div>
            <h2 className="text-lg font-semibold">
              Hospital AI Assistant
            </h2>

            <p className="text-xs text-muted-foreground">
              Voice appointment assistant
            </p>
          </div>

          <button
            type="button"
            onClick={onDisconnected}
            className="rounded-lg px-3 py-2 text-sm hover:bg-muted"
          >
            Close
          </button>
        </div>

        {/* LiveKit Room */}
        <LiveKitRoom
          token={token}
          serverUrl={serverUrl}
          connect={true}
          audio={true}
          video={false}
          onDisconnected={onDisconnected}
        >
          <div className="flex min-h-[420px] flex-col items-center justify-center px-6 py-8">

            {/* AI Circle */}
            <div className="flex h-24 w-24 items-center justify-center rounded-full bg-primary text-2xl font-bold text-primary-foreground">
              AI
            </div>

            <h3 className="mt-6 text-xl font-semibold">
              Hospital Assistant
            </h3>

            <p className="mt-2 max-w-sm text-center text-sm text-muted-foreground">
              Speak naturally. I can help you with
              appointments, availability, cancellations,
              and appointment status.
            </p>

            {/* Microphone */}
            <div className="mt-8">
              <ControlBar
                variation="minimal"
                controls={{
                  microphone: true,
                  camera: false,
                  screenShare: false,
                }}
              />
            </div>

            {/* Agent audio */}
            <RoomAudioRenderer />

          </div>
        </LiveKitRoom>

      </div>
    </div>
  );
}