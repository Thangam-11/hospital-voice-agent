"use client";

import { CalendarPlus, CalendarSearch, Mic } from "lucide-react";
import { useRouter } from "next/navigation";

import { PatientHome } from "@/components/patient/PatientHome";

export default function Home() {
  const router = useRouter();

  return (
    <PatientHome>
      <div className="text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0D9488]">
          <Mic className="h-6 w-6 text-white" />
        </div>
        <h1 className="mt-6 text-3xl font-bold tracking-tight text-slate-900">
          MediVoice AI
        </h1>
        <p className="mt-2 max-w-md text-slate-500">
          Talk to our AI assistant to book appointments, check existing
          bookings, or get hospital information — no account needed.
        </p>
        <div className="mt-8 flex justify-center gap-3">
          <button
            type="button"
            onClick={() => router.push("/appointment")}
            className="flex items-center gap-2 rounded-lg bg-[#0D9488] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0F766E]"
          >
            <CalendarPlus className="h-4 w-4" />
            Book Appointment
          </button>
          <button
            type="button"
            onClick={() => router.push("/check-appointment")}
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
          >
            <CalendarSearch className="h-4 w-4" />
            Check Appointment
          </button>
        </div>
      </div>
    </PatientHome>
  );
}
