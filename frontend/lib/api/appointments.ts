import { apiFetch } from "./client";
import { getRecentAppointments } from "./dashboard";
import type { RecentAppointmentItem, Slot } from "./types";

/** GET /appointments/slots?doctor_id=&date= */
export async function getAppointmentSlots(params: {
  doctorId?: string;
  date?: string;
}): Promise<Slot[]> {
  const query = new URLSearchParams();
  if (params.doctorId) query.set("doctor_id", params.doctorId);
  if (params.date) query.set("date", params.date);
  const qs = query.toString();
  return apiFetch<Slot[]>(`/appointments/slots${qs ? `?${qs}` : ""}`);
}

export interface BookAppointmentPayload {
  patient_id: string;
  doctor_id: string;
  appointment_slot_id: string;
  booking_reason?: string;
}

/** POST /appointments */
export async function bookAppointment(payload: BookAppointmentPayload) {
  return apiFetch("/appointments", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** POST /appointments/{appointment_id}/cancel */
export async function cancelAppointment(appointmentId: string) {
  return apiFetch(`/appointments/${appointmentId}/cancel`, {
    method: "POST",
  });
}

/** GET /appointments/patient/{patient_id} */
export async function getPatientAppointments(patientId: string) {
  return apiFetch(`/appointments/patient/${patientId}`);
}

/**
 * There's no dedicated "list all appointments" endpoint on the backend yet
 * (only /appointments/slots, /appointments/patient/{id}, book, and cancel).
 * Until that's added, the Appointments page reuses the dashboard's
 * recent-appointments endpoint with a high limit. Swap this out once a
 * real GET /appointments listing endpoint exists.
 */
export async function getAllAppointments(
  limit: number = 100,
): Promise<RecentAppointmentItem[]> {
  return getRecentAppointments(limit);
}
