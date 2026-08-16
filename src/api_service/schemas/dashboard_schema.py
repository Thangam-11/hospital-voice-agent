from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_patients: int
    total_active_doctors: int
    appointments_today: int
    upcoming_appointments: int  # Scheduled/Confirmed/Rescheduled, today onward
    ai_calls_today: int


class AppointmentTrendPoint(BaseModel):
    date: date
    count: int


class DepartmentBreakdownItem(BaseModel):
    department: str
    count: int
    percentage: float


class RecentAppointmentItem(BaseModel):
    """Flattened Appointment + AppointmentSlot + Patient + Doctor."""

    id: UUID
    patient_name: str
    doctor_name: str
    department: str
    slot_date: date
    start_time: str
    appointment_status: str


class RecentCallItem(BaseModel):
    id: UUID
    patient_name: Optional[str] = None
    caller_phone: str
    intent: Optional[str] = None
    outcome: Optional[str] = None
    duration_seconds: Optional[int] = None
    started_at: datetime