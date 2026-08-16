// Mirrors src/api_service/schemas/*.py — keep these in sync by hand,
// there's no OpenAPI codegen wired up yet.

export type AppointmentStatus =
  | "Scheduled"
  | "Confirmed"
  | "Completed"
  | "Cancelled"
  | "Rescheduled"
  | "No Show";

export interface Patient {
  id: string;
  full_name: string;
  date_of_birth: string; // ISO date
  phone_number: string;
  gender: string | null;
  email: string | null;
  created_at: string | null;
}

export interface PatientListResponse {
  patients: Patient[];
  count: number;
}

export interface Slot {
  id: string;
  doctor_id: string;
  slot_date: string; // ISO date
  start_time: string; // "HH:MM:SS"
  end_time: string;
  is_available: boolean;
}

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  appointment_slot_id: string;
  appointment_status: AppointmentStatus;
  booking_reason: string | null;
  created_at: string; // ISO datetime
}

export interface AppointmentListResponse {
  appointments: Appointment[];
  count: number;
}

export interface ApiErrorBody {
  detail: string;
}

export interface Doctor {
  id: string;
  doctor_name: string;
  specialization: string;
  department: string;
  qualifications: string;
  experience: number;
  status: boolean;
}

export interface DoctorListResponse {
  doctors: Doctor[];
  count: number;
}

export interface DashboardStats {
  total_patients: number;
  total_active_doctors: number;
  appointments_today: number;
  upcoming_appointments: number;
  ai_calls_today: number;
}

export interface AppointmentTrendPoint {
  date: string; // ISO date
  count: number;
}

export interface DepartmentBreakdownItem {
  department: string;
  count: number;
  percentage: number;
}

export interface RecentAppointmentItem {
  id: string;
  patient_name: string;
  doctor_name: string;
  department: string;
  slot_date: string;
  start_time: string;
  appointment_status: AppointmentStatus;
}

export interface RecentCallItem {
  id: string;
  patient_name: string | null;
  caller_phone: string;
  intent: string | null;
  outcome: string | null;
  duration_seconds: number | null;
  started_at: string; // ISO datetime
}
