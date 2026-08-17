"use client";

import { CalendarDays, Search, X } from "lucide-react";
import { useEffect, useState } from "react";

import { bookAppointment, getAppointmentSlots } from "@/lib/api/appointments";
import { getDoctors } from "@/lib/api/doctors";
import { getPatients } from "@/lib/api/patients";
import type { Doctor, Patient, Slot } from "@/lib/api/types";

interface BookAppointmentModalProps {
  onClose: () => void;
  onBooked: () => void;
}

export function BookAppointmentModal({
  onClose,
  onBooked,
}: BookAppointmentModalProps) {
  // Patient search
  const [patientQuery, setPatientQuery] = useState("");
  const [patientResults, setPatientResults] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  // Doctor + slots
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [doctorId, setDoctorId] = useState("");
  const [date, setDate] = useState("");
  const [slots, setSlots] = useState<Slot[]>([]);
  const [slotId, setSlotId] = useState("");
  const [reason, setReason] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  // Load doctors once
  useEffect(() => {
    getDoctors()
      .then(setDoctors)
      .catch(() => setDoctors([]));
  }, []);

  // Debounced patient search
  useEffect(() => {
    if (patientQuery.trim().length < 2) {
      setPatientResults([]);
      return;
    }
    const timeout = setTimeout(() => {
      getPatients(patientQuery)
        .then(setPatientResults)
        .catch(() => setPatientResults([]));
    }, 250);
    return () => clearTimeout(timeout);
  }, [patientQuery]);

  // Load slots whenever doctor + date are both set
  useEffect(() => {
    if (!doctorId || !date) {
      setSlots([]);
      return;
    }
    getAppointmentSlots({ doctorId, date })
      .then((s) => setSlots(s.filter((slot) => slot.is_available)))
      .catch(() => setSlots([]));
  }, [doctorId, date]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedPatient || !doctorId || !slotId) return;

    setSubmitting(true);
    setError("");

    try {
      await bookAppointment({
        patient_id: selectedPatient.id,
        doctor_id: doctorId,
        appointment_slot_id: slotId,
        booking_reason: reason || undefined,
      });
      setSuccess(true);
      onBooked();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to book appointment.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            Book Appointment
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

        {success ? (
          <div className="py-6 text-center">
            <p className="text-sm font-medium text-emerald-700">
              Appointment booked successfully.
            </p>
            <button
              type="button"
              onClick={onClose}
              className="mt-4 rounded-lg bg-[#0D9488] px-4 py-2 text-sm font-semibold text-white hover:bg-[#0F766E]"
            >
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Patient search */}
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Patient
              </label>
              {selectedPatient ? (
                <div className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2 text-sm">
                  <span className="font-medium text-slate-900">
                    {selectedPatient.full_name}
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedPatient(null);
                      setPatientQuery("");
                    }}
                    className="text-xs text-[#0D9488] hover:underline"
                  >
                    Change
                  </button>
                </div>
              ) : (
                <div className="relative">
                  <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    value={patientQuery}
                    onChange={(e) => setPatientQuery(e.target.value)}
                    placeholder="Search patient by name or phone..."
                    className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
                  />
                  {patientResults.length > 0 && (
                    <div className="absolute z-10 mt-1 w-full rounded-lg border border-slate-200 bg-white shadow-lg">
                      {patientResults.map((p) => (
                        <button
                          type="button"
                          key={p.id}
                          onClick={() => {
                            setSelectedPatient(p);
                            setPatientResults([]);
                          }}
                          className="block w-full px-3 py-2 text-left text-sm hover:bg-slate-50"
                        >
                          <p className="font-medium text-slate-900">
                            {p.full_name}
                          </p>
                          <p className="text-xs text-slate-400">
                            {p.phone_number}
                          </p>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Doctor */}
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Doctor
              </label>
              <select
                required
                value={doctorId}
                onChange={(e) => {
                  setDoctorId(e.target.value);
                  setSlotId("");
                }}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
              >
                <option value="">Select a doctor</option>
                {doctors.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.doctor_name} · {d.department}
                  </option>
                ))}
              </select>
            </div>

            {/* Date */}
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Date
              </label>
              <div className="relative">
                <CalendarDays className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  required
                  type="date"
                  value={date}
                  onChange={(e) => {
                    setDate(e.target.value);
                    setSlotId("");
                  }}
                  className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
                />
              </div>
            </div>

            {/* Slots */}
            {doctorId && date && (
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-500">
                  Available time
                </label>
                {slots.length === 0 ? (
                  <p className="text-xs text-slate-400">
                    No available slots for this date.
                  </p>
                ) : (
                  <div className="grid grid-cols-3 gap-2">
                    {slots.map((slot) => (
                      <button
                        type="button"
                        key={slot.id}
                        onClick={() => setSlotId(slot.id)}
                        className={`rounded-lg border px-2 py-1.5 text-xs font-medium transition-colors ${
                          slotId === slot.id
                            ? "border-[#0D9488] bg-[#0D9488]/10 text-[#0D9488]"
                            : "border-slate-200 text-slate-600 hover:border-slate-300"
                        }`}
                      >
                        {slot.start_time.slice(0, 5)}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Reason */}
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Reason (optional)
              </label>
              <input
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#0D9488]/40 focus:ring-2 focus:ring-[#0D9488]/10"
              />
            </div>

            {error && <p className="text-xs text-red-600">{error}</p>}

            <button
              type="submit"
              disabled={submitting || !selectedPatient || !slotId}
              className="w-full rounded-lg bg-[#0D9488] py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0F766E] disabled:opacity-50"
            >
              {submitting ? "Booking…" : "Confirm Booking"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
