import { apiFetch } from "./client";

export interface ActivityLog {
  id: string;
  event_type: string;
  entity_type: string;
  entity_id?: string | null;
  patient_id?: string | null;
  appointment_id?: string | null;
  actor_type: string;
  description?: string | null;
  metadata?: Record<string, unknown> | null;
  created_at: string;
}

/** GET /activity-logs?limit= */
export async function getActivityLogs(limit: number = 10): Promise<ActivityLog[]> {
  return apiFetch<ActivityLog[]>(`/activity-logs?limit=${limit}`);
}
