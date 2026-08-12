"""
Appointment router. Every endpoint here is a thin HTTP wrapper around
AppointmentService — no business logic lives in this file, just:
  1. parse/validate the request (Pydantic does this automatically)
  2. call the service
  3. translate service exceptions into HTTP status codes
  4. serialize the response (Pydantic does this automatically too)
"""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_engine import get_db
from src.service.appointment_service import AppointmentService
from src.utils.exceptions import (
    AppointmentNotFoundError,
    InvalidAppointmentStateError,
    SlotNotFoundError,
    SlotUnavailableError,
)
from src.api_service.schemas.appointment_schema import (
    AppointmentBookRequest,
    AppointmentListResponse,
    AppointmentResponse,
    SlotResponse,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/slots", response_model=list[SlotResponse])
async def search_slots(
    specialization: Optional[str] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    session: AsyncSession = Depends(get_db),
):
    service = AppointmentService(session)
    slots = await service.find_available_slots(
        specialization=specialization, date_from=date_from, limit=limit
    )
    return slots


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def book_appointment(
    payload: AppointmentBookRequest,
    session: AsyncSession = Depends(get_db),
):
    service = AppointmentService(session)
    try:
        appointment = await service.book_appointment(
            patient_id=payload.patient_id,
            slot_id=payload.slot_id,
            reason=payload.reason,
        )
    except SlotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SlotUnavailableError as e:
        # 409 Conflict: the request is well-formed, but the resource state
        # (slot already taken) prevents fulfilling it right now.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: UUID,
    patient_id: UUID = Query(..., description="Patient requesting the cancellation"),
    session: AsyncSession = Depends(get_db),
):
    service = AppointmentService(session)
    try:
        return await service.cancel_appointment(appointment_id, patient_id)
    except AppointmentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidAppointmentStateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/patient/{patient_id}", response_model=AppointmentListResponse)
async def get_patient_appointments(
    patient_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    service = AppointmentService(session)
    appointments = await service.check_status(patient_id)
    return AppointmentListResponse(appointments=appointments, count=len(appointments))