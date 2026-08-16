"""
Dashboard router — read-only aggregation endpoints for the admin overview
page. Same "no auth yet" caveat as patient.py: fine for local dev, add
auth before exposing this anywhere shared.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_engine import get_db
from src.service.dashboard_service import DashboardService
from src.api_service.schemas.dashboard_schema import (
    AppointmentTrendPoint,
    DashboardStats,
    DepartmentBreakdownItem,
    RecentAppointmentItem,
    RecentCallItem,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(session: AsyncSession = Depends(get_db)):
    service = DashboardService(session)
    return await service.get_stats()


@router.get("/appointment-trend", response_model=list[AppointmentTrendPoint])
async def get_appointment_trend(
    days: int = Query(default=7, ge=1, le=30),
    session: AsyncSession = Depends(get_db),
):
    service = DashboardService(session)
    return await service.get_appointment_trend(days=days)


@router.get("/department-breakdown", response_model=list[DepartmentBreakdownItem])
async def get_department_breakdown(session: AsyncSession = Depends(get_db)):
    service = DashboardService(session)
    return await service.get_department_breakdown()


@router.get("/recent-appointments", response_model=list[RecentAppointmentItem])
async def get_recent_appointments(
    limit: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_db),
):
    service = DashboardService(session)
    rows = await service.get_recent_appointments(limit=limit)

    return [
        RecentAppointmentItem(
            id=appointment.id,
            patient_name=patient.full_name,
            doctor_name=doctor.doctor_name,
            department=doctor.department,
            slot_date=slot.slot_date,
            start_time=slot.start_time.isoformat(timespec="minutes"),
            appointment_status=appointment.appointment_status.value,
        )
        for appointment, slot, patient, doctor in rows
    ]


@router.get("/recent-calls", response_model=list[RecentCallItem])
async def get_recent_calls(
    limit: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_db),
):
    service = DashboardService(session)
    rows = await service.get_recent_calls(limit=limit)

    return [
        RecentCallItem(
            id=call.id,
            patient_name=patient.full_name if patient else None,
            caller_phone=call.caller_phone,
            intent=call.intent,
            outcome=call.outcome.value if call.outcome else None,
            duration_seconds=call.duration_seconds,
            started_at=call.started_at,
        )
        for call, patient in rows
    ]