"use client";

import { CalendarDays, CheckCircle2, Clock3 } from "lucide-react";
import { useEffect, useState } from "react";

import { getRecentAppointments } from "@/lib/api/dashboard";
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
        STATUS_STYLES[status] ?? "bg-muted text-muted-foreground"
      }`}
    >
      <Icon className="h-3.5 w-3.5" />
      {status}
    </span>
  );
}

export function AppointmentsCard() {
  const [appointments, setAppointments] = useState<RecentAppointmentItem[]>(
    [],
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getRecentAppointments(5)
      .then(setAppointments)
      .catch((err) =>
        setError(
          err instanceof Error ? err.message : "Failed to load appointments.",
        ),
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="rounded-xl border bg-white">
      <div className="flex items-center justify-between border-b px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold">Recent Appointments</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Latest patient appointments
          </p>
        </div>

        <a
          href="/appointments"
          className="text-xs font-medium text-primary hover:underline"
        >
          View all
        </a>
      </div>

      {error && <div className="px-5 py-4 text-sm text-red-700">{error}</div>}

      <div className="divide-y">
        {loading ? (
          <div className="px-5 py-8 text-center text-sm text-muted-foreground">
            Loading…
          </div>
        ) : appointments.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-muted-foreground">
            No appointments yet.
          </div>
        ) : (
          appointments.map((appointment) => (
            <div
              key={appointment.id}
              className="flex items-center gap-4 px-5 py-4 transition-colors hover:bg-muted/30"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                {appointment.patient_name.charAt(0)}
              </div>

              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">
                  {appointment.patient_name}
                </p>
                <p className="mt-0.5 truncate text-xs text-muted-foreground">
                  {appointment.doctor_name} · {appointment.department}
                </p>
              </div>

              <div className="hidden items-center gap-1.5 text-xs text-muted-foreground sm:flex">
                <CalendarDays className="h-3.5 w-3.5" />
                {appointment.slot_date} · {appointment.start_time}
              </div>

              <StatusBadge status={appointment.appointment_status} />
            </div>
          ))
        )}
      </div>
    </div>
  );
}
