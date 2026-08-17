"use client";

import { CalendarDays, CalendarPlus, CheckCircle2, Clock3 } from "lucide-react";
import { useEffect, useState } from "react";

import { BookAppointmentModal } from "@/components/appointments/book-appointment-modal";
import { getAllAppointments } from "@/lib/api/appointments";
import type { RecentAppointmentItem } from "@/lib/api/types";

const STATUS_STYLES: Record<string, string> = {
  Completed: "bg-emerald-50 text-emerald-700",
  Confirmed: "bg-blue-50 text-blue-700",
  Scheduled: "bg-amber-50 text-amber-700",
  Rescheduled: "bg-amber-50 text-amber-700",
  Cancelled: "bg-red-50 text-red-700",
  "No Show": "bg-red-50 text-red-700",
};

function StatusBadge({ status }: { status: string }) {
  const Icon =
    status === "Completed" || status === "Confirmed" ? CheckCircle2 : Clock3;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${
        STATUS_STYLES[status] ?? "bg-slate-100 text-slate-500"
      }`}
    >
      <Icon className="h-3.5 w-3.5" />
      {status}
    </span>
  );
}

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<
    RecentAppointmentItem[] | null
  >(null);
  const [error, setError] = useState("");
  const [showBooking, setShowBooking] = useState(false);

  function reload() {
    getAllAppointments(20)
      .then(setAppointments)
      .catch((err) =>
        setError(
          err instanceof Error ? err.message : "Failed to load appointments.",
        ),
      );
  }

  useEffect(reload, []);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          {appointments ? `${appointments.length} appointments` : ""}
        </p>

        <button
          type="button"
          onClick={() => setShowBooking(true)}
          className="flex items-center gap-1.5 rounded-lg bg-[#0D9488] px-3.5 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#0F766E]"
        >
          <CalendarPlus className="h-4 w-4" />
          Book Appointment
        </button>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        {error ? (
          <div className="p-6 text-sm text-red-700">{error}</div>
        ) : appointments === null ? (
          <div className="p-10 text-center text-sm text-slate-400">
            Loading…
          </div>
        ) : appointments.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-400">
            No appointments found.
          </div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                <th className="px-5 py-3 font-medium">Patient</th>
                <th className="px-5 py-3 font-medium">Doctor</th>
                <th className="px-5 py-3 font-medium">Department</th>
                <th className="px-5 py-3 font-medium">Date &amp; Time</th>
                <th className="px-5 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {appointments.map((appt) => (
                <tr key={appt.id} className="hover:bg-slate-50/60">
                  <td className="px-5 py-3.5 font-medium text-slate-900">
                    {appt.patient_name}
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    {appt.doctor_name}
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    {appt.department}
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    <span className="inline-flex items-center gap-1.5">
                      <CalendarDays className="h-3.5 w-3.5 text-slate-400" />
                      {appt.slot_date} · {appt.start_time.slice(0, 5)}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={appt.appointment_status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showBooking && (
        <BookAppointmentModal
          onClose={() => setShowBooking(false)}
          onBooked={() => reload()}
        />
      )}
    </div>
  );
}
