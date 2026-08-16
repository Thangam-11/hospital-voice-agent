from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    doctor_name: str
    specialization: str
    department: str
    qualifications: str
    experience: int
    status: bool


class DoctorListResponse(BaseModel):
    doctors: list[DoctorResponse]
    count: int


class DoctorAppointmentHistoryItem(BaseModel):
    """
    Flattened Appointment + AppointmentSlot + Patient — built manually in
    the router from a joined query, not via from_attributes, since it
    spans three ORM models.
    """

    id: UUID
    patient_id: UUID
    patient_name: str
    slot_date: str
    start_time: str
    end_time: str
    appointment_status: str
    booking_reason: Optional[str] = None
    created_at: str


class DoctorAppointmentHistoryResponse(BaseModel):
    doctor_id: UUID
    appointments: list[DoctorAppointmentHistoryItem]
    count: int