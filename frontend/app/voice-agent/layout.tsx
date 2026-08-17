import { AppShell } from "@/components/layout/app-shell";

export default function VoiceAgentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AppShell
      title="Voice Agent"
      subtitle="Talk to the AI hospital assistant"
    >
      {children}
    </AppShell>
  );
}