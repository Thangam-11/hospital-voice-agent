"use client";

import {
  CalendarDays,
  ChevronDown,
  Clock3,
  Plus,
  Search,
} from "lucide-react";
import { useState } from "react";

const appointments = [
  {
    id: "APT-1001",
    patient: "Ravi Kumar",
    doctor: "Dr. Arjun Patel",
    department: "Cardiology",
    date: "Aug 14, 2026",
    time: "10:00 AM",
    status: "Completed",
    type: "In-person",
  },
  {
    id: "APT-1002",
    patient: "Priya Sharma",
    doctor: "Dr. Neha Gupta",
    department: "General Medicine",
    date: "Aug 14, 2026",
    time: "10:30 AM",
    status: "Confirmed",
    type: "In-person",
  },
  {
    id: "APT-1003",
    patient: "Arun Singh",
    doctor: "Dr. Mohan Reddy",
    department: "Neurology",
    date: "Aug 14, 2026",
    time: "11:00 AM",
    status: "Upcoming",
    type: "In-person",
  },
  {
    id: "APT-1004",
    patient: "Meena Devi",
    doctor: "Dr. Kavita Joshi",
    department: "Pediatrics",
    date: "Aug 14, 2026",
    time: "11:30 AM",
    status: "Upcoming",
    type: "Voice Booking",
  },
  {
    id: "APT-1005",
    patient: "Suresh Kumar",
    doctor: "Dr. Arjun Patel",
    department: "Cardiology",
    date: "Aug 14, 2026",
    time: "12:00 PM",
    status: "Confirmed",
    type: "Web Booking",
  },
];

function StatusBadge({ status }: { status: string }) {
  const styles = {
    Completed: "bg-emerald-50 text-emerald-700",
    Confirmed: "bg-blue-50 text-blue-700",
    Upcoming: "bg-amber-50 text-amber-700",
    Cancelled: "bg-red-50 text-red-700",
  };

  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
        styles[status as keyof typeof styles] ??
        "bg-muted text-muted-foreground"
      }`}
    >
      {status}
    </span>
  );
}

export default function AppointmentsPage() {
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);

  const filteredAppointments = appointments.filter(
    (appointment) =>
      appointment.patient
        .toLowerCase()
        .includes(search.toLowerCase()) ||
      appointment.doctor
        .toLowerCase()
        .includes(search.toLowerCase()) ||
      appointment.department
        .toLowerCase()
        .includes(search.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-[1600px] px-6 py-8">
      {/* Page heading */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Appointments
          </h1>

          <p className="mt-1 text-sm text-muted-foreground">
            Manage patient appointments across all booking channels.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow-sm hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          New Appointment
        </button>
      </div>

      {/* Summary */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-muted-foreground">
            Total Today
          </p>
          <p className="mt-2 text-2xl font-semibold">45</p>
        </div>

        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-muted-foreground">
            Confirmed
          </p>
          <p className="mt-2 text-2xl font-semibold">24</p>
        </div>

        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-muted-foreground">
            Upcoming
          </p>
          <p className="mt-2 text-2xl font-semibold">18</p>
        </div>

        <div className="rounded-xl border bg-white p-5">
          <p className="text-sm text-muted-foreground">
            Completed
          </p>
          <p className="mt-2 text-2xl font-semibold">21</p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-4 rounded-xl border bg-white p-4">
        <div className="flex flex-col gap-3 lg:flex-row">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search patient, doctor, or department..."
              className="h-10 w-full rounded-lg border bg-white pl-9 pr-3 text-sm outline-none placeholder:text-muted-foreground focus:border-primary"
            />
          </div>

          {/* Date */}
          <button
            type="button"
            className="inline-flex h-10 items-center justify-between gap-3 rounded-lg border px-3 text-sm text-muted-foreground hover:bg-muted"
          >
            <span className="flex items-center gap-2">
              <CalendarDays className="h-4 w-4" />
              Today
            </span>

            <ChevronDown className="h-4 w-4" />
          </button>

          {/* Status */}
          <button
            type="button"
            className="inline-flex h-10 items-center justify-between gap-3 rounded-lg border px-3 text-sm text-muted-foreground hover:bg-muted"
          >
            <span>Status: All</span>
            <ChevronDown className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Appointment table */}
      <div className="overflow-hidden rounded-xl border bg-white">
        <div className="border-b px-5 py-4">
          <h2 className="text-sm font-semibold">
            Today&apos;s Appointments
          </h2>

          <p className="mt-1 text-xs text-muted-foreground">
            {filteredAppointments.length} appointments shown
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-sm">
            <thead>
              <tr className="border-b bg-muted/20">
                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Patient
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Doctor
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Department
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Date & Time
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Channel
                </th>

                <th className="px-5 py-3 text-left text-xs font-medium text-muted-foreground">
                  Status
                </th>
              </tr>
            </thead>

            <tbody className="divide-y">
              {filteredAppointments.map((appointment) => (
                <tr
                  key={appointment.id}
                  className="transition-colors hover:bg-muted/20"
                >
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                        {appointment.patient.charAt(0)}
                      </div>

                      <div>
                        <p className="font-medium">
                          {appointment.patient}
                        </p>

                        <p className="text-xs text-muted-foreground">
                          {appointment.id}
                        </p>
                      </div>
                    </div>
                  </td>

                  <td className="px-5 py-4">
                    <p className="font-medium">
                      {appointment.doctor}
                    </p>
                  </td>

                  <td className="px-5 py-4 text-muted-foreground">
                    {appointment.department}
                  </td>

                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <Clock3 className="h-4 w-4 text-muted-foreground" />

                      <div>
                        <p>{appointment.time}</p>
                        <p className="text-xs text-muted-foreground">
                          {appointment.date}
                        </p>
                      </div>
                    </div>
                  </td>

                  <td className="px-5 py-4">
                    <span className="rounded-full bg-muted px-2.5 py-1 text-xs">
                      {appointment.type}
                    </span>
                  </td>

                  <td className="px-5 py-4">
                    <StatusBadge status={appointment.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* New appointment modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg rounded-2xl border bg-white shadow-xl">
            <div className="border-b px-6 py-5">
              <h2 className="text-lg font-semibold">
                New Appointment
              </h2>

              <p className="mt-1 text-sm text-muted-foreground">
                Create an appointment manually from the dashboard.
              </p>
            </div>

            <div className="space-y-4 p-6">
              <div>
                <label className="mb-1.5 block text-sm font-medium">
                  Patient
                </label>

                <select className="h-10 w-full rounded-lg border bg-white px-3 text-sm">
                  <option>Select patient</option>
                  <option>Ravi Kumar</option>
                  <option>Priya Sharma</option>
                  <option>Arun Singh</option>
                  <option>Meena Devi</option>
                </select>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium">
                  Department
                </label>

                <select className="h-10 w-full rounded-lg border bg-white px-3 text-sm">
                  <option>Cardiology</option>
                  <option>General Medicine</option>
                  <option>Neurology</option>
                  <option>Pediatrics</option>
                  <option>Orthopedics</option>
                </select>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium">
                  Doctor
                </label>

                <select className="h-10 w-full rounded-lg border bg-white px-3 text-sm">
                  <option>Dr. Arjun Patel</option>
                  <option>Dr. Neha Gupta</option>
                  <option>Dr. Mohan Reddy</option>
                  <option>Dr. Kavita Joshi</option>
                </select>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1.5 block text-sm font-medium">
                    Date
                  </label>

                  <input
                    type="date"
                    className="h-10 w-full rounded-lg border bg-white px-3 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium">
                    Time
                  </label>

                  <select className="h-10 w-full rounded-lg border bg-white px-3 text-sm">
                    <option>10:00 AM</option>
                    <option>10:30 AM</option>
                    <option>11:00 AM</option>
                    <option>11:30 AM</option>
                    <option>12:00 PM</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 border-t px-6 py-4">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                Confirm Appointment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}