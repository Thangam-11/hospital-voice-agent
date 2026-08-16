"""
Doctor router. Read-only, same pattern as patient.py: thin HTTP wrapper
around DoctorService.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_engine import get_db
from src.database.models import AppointmentStatus
from src.service.doctor_service import DoctorService
from src.api_service.schemas.doctor_schema import (
    DoctorAppointmentHistoryItem,
    DoctorAppointmentHistoryResponse,
    DoctorListResponse,
    DoctorResponse,
)

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=DoctorListResponse)
async def list_doctors(
    department: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_db),
):
    service = DoctorService(session)
    doctors = await service.list_doctors(department=department)
    return DoctorListResponse(doctors=doctors, count=len(doctors))


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    service = DoctorService(session)
    doctor = await service.find_by_id(doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")
    return doctor


@router.get(
    "/{doctor_id}/appointments",
    response_model=DoctorAppointmentHistoryResponse,
)
async def get_doctor_appointment_history(
    doctor_id: UUID,
    status_filter: Optional[AppointmentStatus] = Query(
        default=None,
        alias="status",
        description="Filter to one appointment status, e.g. Completed.",
    ),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    service = DoctorService(session)

    doctor = await service.find_by_id(doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

    rows = await service.get_appointment_history(
        doctor_id, status_filter=status_filter, limit=limit, offset=offset
    )

    items = [
        DoctorAppointmentHistoryItem(
            id=appointment.id,
            patient_id=patient.id,
            patient_name=patient.full_name,
            slot_date=slot.slot_date.isoformat(),
            start_time=slot.start_time.isoformat(timespec="minutes"),
            end_time=slot.end_time.isoformat(timespec="minutes"),
            appointment_status=appointment.appointment_status.value,
            booking_reason=appointment.booking_reason,
            created_at=appointment.created_at.isoformat(),
        )
        for appointment, slot, patient in rows
    ]

    return DoctorAppointmentHistoryResponse(
        doctor_id=doctor_id, appointments=items, count=len(items)
    )