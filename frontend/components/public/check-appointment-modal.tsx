"use client";

import { CalendarDays, Search, X } from "lucide-react";
import { useState } from "react";

import { getPatientAppointments } from "@/lib/api/appointments";
import { getPatients } from "@/lib/api/patients";
import type { RecentAppointmentItem } from "@/lib/api/types";

export function CheckAppointmentModal({
  onClose,
}: {
  onClose: () => void;
}) {
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [appointments, setAppointments] = useState<
    RecentAppointmentItem[] | null
  >(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!phone.trim()) return;

    setLoading(true);
    setError("");
    setAppointments(null);

    try {
      const matches = await getPatients(phone.trim());
      const patient = matches.find((p) => p.phone_number === phone.trim());

      if (!patient) {
        setError("No patient found with that phone number.");
        return;
      }

      const data = await getPatientAppointments(patient.id);
      // Response shape depends on your backend's
      // GET /appointments/patient/{patient_id} — adjust if it
      // returns { appointments: [...] } instead of a bare array.
      const list = Array.isArray(data)
        ? (data as unknown as RecentAppointmentItem[])
        : ((data as any)?.appointments ?? []);
      setAppointments(list);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to look up appointments.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            Check Appointment
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="rounded-full p-1.5 text-slate-400 hover:bg-slate-100"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            required
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Enter your phone number"
            className="flex-1 rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
          />
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-1.5 rounded-lg bg-[#0D9488] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0F766E] disabled:opacity-60"
          >
            <Search className="h-4 w-4" />
            {loading ? "…" : "Search"}
          </button>
        </form>

        {error && <p className="mt-3 text-xs text-red-600">{error}</p>}

        {appointments && (
          <div className="mt-4 max-h-72 space-y-2 overflow-y-auto">
            {appointments.length === 0 ? (
              <p className="py-4 text-center text-sm text-slate-400">
                No appointments found.
              </p>
            ) : (
              appointments.map((appt) => (
                <div
                  key={appt.id}
                  className="rounded-lg border border-slate-200 px-3.5 py-2.5"
                >
                  <p className="text-sm font-medium text-slate-900">
                    {appt.doctor_name} · {appt.department}
                  </p>
                  <p className="mt-0.5 flex items-center gap-1.5 text-xs text-slate-400">
                    <CalendarDays className="h-3.5 w-3.5" />
                    {appt.slot_date} · {appt.start_time?.slice(0, 5)}
                  </p>
                  <p className="mt-1 text-xs font-medium text-slate-500">
                    {appt.appointment_status}
                  </p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
