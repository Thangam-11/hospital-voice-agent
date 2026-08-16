import { apiFetch } from "./client";
import type {
  AppointmentTrendPoint,
  DashboardStats,
  DepartmentBreakdownItem,
  RecentAppointmentItem,
  RecentCallItem,
} from "./types";

/** GET /dashboard/stats */
export async function getDashboardStats(): Promise<DashboardStats> {
  return apiFetch<DashboardStats>("/dashboard/stats");
}

/** GET /dashboard/appointment-trend */
export async function getAppointmentTrend(
  days: number = 7,
): Promise<AppointmentTrendPoint[]> {
  return apiFetch<AppointmentTrendPoint[]>(
    `/dashboard/appointment-trend?days=${days}`,
  );
}

/** GET /dashboard/department-breakdown */
export async function getDepartmentBreakdown(): Promise<
  DepartmentBreakdownItem[]
> {
  return apiFetch<DepartmentBreakdownItem[]>(
    "/dashboard/department-breakdown",
  );
}

/** GET /dashboard/recent-appointments */
export async function getRecentAppointments(
  limit: number = 5,
): Promise<RecentAppointmentItem[]> {
  return apiFetch<RecentAppointmentItem[]>(
    `/dashboard/recent-appointments?limit=${limit}`,
  );
}

/** GET /dashboard/recent-calls */
export async function getRecentCalls(
  limit: number = 5,
): Promise<RecentCallItem[]> {
  return apiFetch<RecentCallItem[]>(`/dashboard/recent-calls?limit=${limit}`);
}
