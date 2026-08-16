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
