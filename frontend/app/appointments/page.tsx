"use client";

import {
  CalendarDays,
  ChevronDown,
  Clock3,
  Mic,
  Plus,
  Search,
} from "lucide-react";

import { useState } from "react";

import VoiceAssistant from "@/components/voice/VoiceAssistant";
import { createVoiceToken } from "@/lib/api/livekit";

type Appointment = {
  id: string;
  patient: string;
  doctor: string;
  department: string;
  date: string;
  time: string;
  status: "Completed" | "Confirmed" | "Upcoming" | "Cancelled";
};

const appointments: Appointment[] = [
  {
    id: "1",
    patient: "John Doe",
    doctor: "Dr. Sarah Lee",
    department: "Cardiology",
    date: "2026-08-14",
    time: "10:00 AM",
    status: "Confirmed",
  },
  {
    id: "2",
    patient: "Jane Smith",
    doctor: "Dr. Alan Grant",
    department: "Orthopedics",
    date: "2026-08-15",
    time: "2:30 PM",
    status: "Upcoming",
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
  // ============================================================
  // EXISTING PAGE STATE
  // ============================================================

  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);

  // ============================================================
  // LIVEKIT STATE
  // ============================================================

  const [showVoiceAssistant, setShowVoiceAssistant] = useState(false);
  const [voiceToken, setVoiceToken] = useState<string | null>(null);
  const [voiceServerUrl, setVoiceServerUrl] = useState<string | null>(null);
  const [voiceLoading, setVoiceLoading] = useState(false);
  const [voiceError, setVoiceError] = useState("");

  // ============================================================
  // START VOICE ASSISTANT
  // ============================================================

  const startVoiceAssistant = async () => {
    try {
      setVoiceLoading(true);
      setVoiceError("");

      const data = await createVoiceToken("Hospital Patient");

      setVoiceToken(data.participant_token);
      setVoiceServerUrl(data.server_url);
      setShowVoiceAssistant(true);
    } catch (error) {
      console.error("Failed to start voice assistant:", error);

      setVoiceError(
        error instanceof Error
          ? error.message
          : "Unable to start voice assistant.",
      );
    } finally {
      setVoiceLoading(false);
    }
  };

  // ============================================================
  // CLOSE VOICE ASSISTANT
  // ============================================================

  const closeVoiceAssistant = () => {
    setShowVoiceAssistant(false);
    setVoiceToken(null);
    setVoiceServerUrl(null);
    setVoiceError("");
  };

  // ============================================================
  // EXISTING APPOINTMENT FILTER
  // ============================================================

  const filteredAppointments = appointments.filter(
    (appointment) =>
      appointment.patient.toLowerCase().includes(search.toLowerCase()) ||
      appointment.doctor.toLowerCase().includes(search.toLowerCase()) ||
      appointment.department.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Appointments</h1>
          <p className="text-sm text-muted-foreground">
            View and manage patient appointments.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={startVoiceAssistant}
            disabled={voiceLoading}
            className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
          >
            <Mic className="h-4 w-4" />
            {voiceLoading ? "Starting…" : "Voice Assistant"}
          </button>

          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
          >
            <Plus className="h-4 w-4" />
            New Appointment
          </button>
        </div>
      </div>

      {voiceError && (
        <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
          {voiceError}
        </div>
      )}

      {/* Search + Filters */}
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by patient, doctor, or department"
            className="w-full rounded-lg border py-2 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-primary/30"
          />
        </div>

        <button className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium hover:bg-muted">
          <CalendarDays className="h-4 w-4" />
          Date
          <ChevronDown className="h-4 w-4" />
        </button>

        <button className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium hover:bg-muted">
          Status
          <ChevronDown className="h-4 w-4" />
        </button>
      </div>

      {/* Appointments Table */}
      <div className="overflow-hidden rounded-xl border">
        <table className="w-full text-left text-sm">
          <thead className="bg-muted/50 text-muted-foreground">
            <tr>
              <th className="px-4 py-3 font-medium">Patient</th>
              <th className="px-4 py-3 font-medium">Doctor</th>
              <th className="px-4 py-3 font-medium">Department</th>
              <th className="px-4 py-3 font-medium">Date & Time</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredAppointments.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-4 py-8 text-center text-muted-foreground"
                >
                  No appointments found.
                </td>
              </tr>
            ) : (
              filteredAppointments.map((appointment) => (
                <tr key={appointment.id} className="border-t">
                  <td className="px-4 py-3 font-medium">
                    {appointment.patient}
                  </td>
                  <td className="px-4 py-3">{appointment.doctor}</td>
                  <td className="px-4 py-3">{appointment.department}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                      <Clock3 className="h-3.5 w-3.5" />
                      {appointment.date} · {appointment.time}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={appointment.status} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Voice Assistant Overlay */}
      {showVoiceAssistant && voiceToken && voiceServerUrl && (
        <VoiceAssistant
          token={voiceToken}
          serverUrl={voiceServerUrl}
          onClose={closeVoiceAssistant}
        />
      )}
    </div>
  );
}