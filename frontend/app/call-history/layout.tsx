import { AppShell } from "@/components/layout/app-shell";

export default function CallHistoryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AppShell title="Call History" subtitle="All AI voice agent calls">
      {children}
    </AppShell>
  );
}
