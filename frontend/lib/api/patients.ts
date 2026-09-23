import { apiFetch } from "./client";
import type { Patient, PatientListResponse } from "./types";

/** GET /patients?search= */
export async function getPatients(search?: string): Promise<Patient[]> {
  const query = search ? `?search=${encodeURIComponent(search)}` : "";
  const data = await apiFetch<PatientListResponse>(`/patients${query}`);
  return data.patients;
}

/** GET /patients/{patient_id} */
export async function getPatient(patientId: string): Promise<Patient> {
  return apiFetch<Patient>(`/patients/${patientId}`);
}

export interface CreatePatientPayload {
  full_name: string;
  date_of_birth: string; // ISO date, e.g. "1990-05-14"
  phone_number: string;
  gender?: string;
  email?: string;
}

/**
 * POST /patients
 * NOT CONFIRMED in your backend's Swagger list — only GET /patients and
 * GET /patients/{id} were shown. Check http://127.0.0.1:8000/docs for a
 * POST /patients route before relying on this; add it on the backend if
 * it's missing.
 */
export async function createPatient(
  payload: CreatePatientPayload,
): Promise<Patient> {
  return apiFetch<Patient>("/patients", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
