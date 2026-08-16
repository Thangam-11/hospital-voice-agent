import { apiFetch } from "./client";
import type { Doctor, DoctorListResponse, AppointmentListResponse } from "./types";

/** GET /doctors */
export async function getDoctors(): Promise<Doctor[]> {
  const data = await apiFetch<DoctorListResponse>("/doctors");
  return data.doctors;
}

/** GET /doctors/{doctor_id} */
export async function getDoctor(doctorId: string): Promise<Doctor> {
  return apiFetch<Doctor>(`/doctors/${doctorId}`);
}

/** GET /doctors/{doctor_id}/appointments */
export async function getDoctorAppointments(doctorId: string) {
  return apiFetch<AppointmentListResponse>(
    `/doctors/${doctorId}/appointments`,
  );
}
