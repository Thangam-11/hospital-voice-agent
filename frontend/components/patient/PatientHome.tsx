"use client";

import { usePathname, useRouter } from "next/navigation";

import { PatientSidebar } from "@/components/public/patient-sidebar";
import type { PatientNavKey } from "@/components/public/patient-sidebar";

const ROUTE_FOR_KEY: Record<PatientNavKey, string> = {
  talk: "/voice-agent",
  book: "/appointment",
  check: "/check-appointment",
  info: "/hospital-info",
};

const KEY_FOR_ROUTE: Record<string, PatientNavKey> = {
  "/voice-agent": "talk",
  "/appointment": "book",
  "/check-appointment": "check",
  "/hospital-info": "info",
};

export function PatientHome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname() || "/";
  const router = useRouter();
  const active = KEY_FOR_ROUTE[pathname] ?? null;

  function handleSelect(key: PatientNavKey) {
    router.push(ROUTE_FOR_KEY[key]);
  }

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <PatientSidebar active={active} onSelect={handleSelect} />
      <main className="flex flex-1 items-center justify-center p-8">
        {children}
      </main>
    </div>
  );
}
