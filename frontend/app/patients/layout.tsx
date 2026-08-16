import { AppShell } from "@/components/layout/app-shell";

export default function PatientsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AppShell title="Patients" subtitle="All registered patients">
      {children}
    </AppShell>
  );
}
