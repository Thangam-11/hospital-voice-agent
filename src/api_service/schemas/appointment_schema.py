"""
Pydantic schemas for the appointment endpoints.

These are deliberately separate from src/database/models.py. The DB models
describe how data is stored; these describe what the API accepts and
returns. Keeping them apart means you can change a column name in Postgres
without silently changing your API contract, and vice versa.
"""

from datetime import date, datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.database.models import AppointmentStatus


# ---------------------------------------------------------------------------
# Slots
# ---------------------------------------------------------------------------

class SlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    doctor_id: UUID
    slot_date: date
    start_time: time
    end_time: time
    is_available: bool


class SlotSearchQuery(BaseModel):
    """Not used directly as a request body — mirrors the query params the
    router accepts, kept here so the shape is documented in one place."""
    specialization: Optional[str] = Field(default=None, description="e.g. Cardiology")
    date_from: Optional[date] = Field(default=None, description="Earliest date to search from")
    limit: int = Field(default=10, ge=1, le=50)


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------

class AppointmentBookRequest(BaseModel):
    patient_id: UUID
    slot_id: UUID
    reason: Optional[str] = Field(default=None, max_length=500)


class AppointmentRescheduleRequest(BaseModel):
    new_slot_id: UUID


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    doctor_id: UUID
    appointment_slot_id: UUID
    appointment_status: AppointmentStatus
    booking_reason: Optional[str]
    created_at: datetime


class AppointmentListResponse(BaseModel):
    appointments: list[AppointmentResponse]
    count: int


# ---------------------------------------------------------------------------
# Errors — consistent shape for every failure this router can return
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    detail: str