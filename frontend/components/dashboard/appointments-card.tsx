import {
  CalendarDays,
  CheckCircle2,
  Clock3,
} from "lucide-react";

const appointments = [
  {
    patient: "Ravi Kumar",
    doctor: "Dr. Arjun Patel",
    department: "Cardiology",
    time: "10:00 AM",
    status: "Completed",
  },
  {
    patient: "Priya Sharma",
    doctor: "Dr. Neha Gupta",
    department: "General Medicine",
    time: "10:30 AM",
    status: "Confirmed",
  },
  {
    patient: "Arun Singh",
    doctor: "Dr. Mohan Reddy",
    department: "Neurology",
    time: "11:00 AM",
    status: "Upcoming",
  },
  {
    patient: "Meena Devi",
    doctor: "Dr. Kavita Joshi",
    department: "Pediatrics",
    time: "11:30 AM",
    status: "Upcoming",
  },
];

function StatusBadge({ status }: { status: string }) {
  if (status === "Completed") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
        <CheckCircle2 className="h-3.5 w-3.5" />
        Completed
      </span>
    );
  }

  if (status === "Confirmed") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
        <CheckCircle2 className="h-3.5 w-3.5" />
        Confirmed
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
      <Clock3 className="h-3.5 w-3.5" />
      Upcoming
    </span>
  );
}

export function AppointmentsCard() {
  return (
    <div className="rounded-xl border bg-white">
      {/* Header */}
      <div className="flex items-center justify-between border-b px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold">
            Recent Appointments
          </h2>

          <p className="mt-1 text-xs text-muted-foreground">
            Latest patient appointments
          </p>
        </div>

        <button
          type="button"
          className="text-xs font-medium text-primary hover:underline"
        >
          View all
        </button>
      </div>

      {/* Appointments */}
      <div className="divide-y">
        {appointments.map((appointment) => (
          <div
            key={`${appointment.patient}-${appointment.time}`}
            className="flex items-center gap-4 px-5 py-4 transition-colors hover:bg-muted/30"
          >
            {/* Patient avatar */}
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
              {appointment.patient.charAt(0)}
            </div>

            {/* Patient information */}
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">
                {appointment.patient}
              </p>

              <p className="mt-0.5 truncate text-xs text-muted-foreground">
                {appointment.doctor} · {appointment.department}
              </p>
            </div>

            {/* Time */}
            <div className="hidden items-center gap-1.5 text-xs text-muted-foreground sm:flex">
              <CalendarDays className="h-3.5 w-3.5" />
              {appointment.time}
            </div>

            {/* Status */}
            <StatusBadge status={appointment.status} />
          </div>
        ))}
      </div>
    </div>
  );
}