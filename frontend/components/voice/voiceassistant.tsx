"use client";

import "@livekit/components-styles";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  BarVisualizer,
  DisconnectButton,
} from "@livekit/components-react";
import { useEffect } from "react";

interface VoiceAssistantProps {
  token: string;
  serverUrl: string;
  onClose: () => void;
}

export default function VoiceAssistant({
  token,
  serverUrl,
  onClose,
}: VoiceAssistantProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <LiveKitRoom
          token={token}
          serverUrl={serverUrl}
          connect={true}
          audio={true}
          video={false}
          onDisconnected={onClose}
          data-lk-theme="default"
        >
          <VoiceAssistantUI onClose={onClose} />
          <RoomAudioRenderer />
        </LiveKitRoom>
      </div>
    </div>
  );
}

function VoiceAssistantUI({ onClose }: { onClose: () => void }) {
  const { state, audioTrack } = useVoiceAssistant();

  useEffect(() => {
    console.log("Voice assistant state:", state);
  }, [state]);

  return (
    <div className="flex flex-col items-center gap-4">
      <h2 className="text-base font-semibold text-slate-900">
        Voice Assistant
      </h2>

      <p className="text-sm capitalize text-slate-500">
        {state === "listening" && "Listening..."}
        {state === "thinking" && "Thinking..."}
        {state === "speaking" && "Speaking..."}
        {state === "connecting" && "Connecting..."}
        {state === "disconnected" && "Disconnected"}
        {state === "initializing" && "Initializing..."}
      </p>

      <div className="h-24 w-full">
        <BarVisualizer
          state={state}
          barCount={7}
          trackRef={audioTrack}
          className="h-24 w-full"
        />
      </div>

      <DisconnectButton
        onClick={onClose}
        className="mt-2 rounded-full bg-red-500 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-600"
      >
        End Call
      </DisconnectButton>
    </div>
  );
}