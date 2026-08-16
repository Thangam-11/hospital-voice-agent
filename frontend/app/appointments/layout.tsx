import { AppShell } from "@/components/layout/app-shell";

export default function AppointmentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AppShell title="Appointments" subtitle="All scheduled appointments">
      {children}
    </AppShell>
  );
}
