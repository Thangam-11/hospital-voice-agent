"use client";

import { PatientHome } from "@/components/patient/PatientHome";
import { VoiceAgent } from "@/components/patient/VoiceAgent";

export default function PublicVoiceAgentPage() {
  return (
    <PatientHome>
      <VoiceAgent />
    </PatientHome>
  );
}
