"""
Service layer for the admin dashboard/overview page. Every method here is
a read-only aggregation query — no business rules, so nothing here belongs
in AppointmentService/PatientService.
"""

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    Appointment,
    AppointmentSlot,
    AppointmentStatus,
    CallLog,
    Doctor,
    Patient,
)
from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)

# "Upcoming" on the dashboard means booked and not yet resolved either way.
ACTIVE_STATUSES = (
    AppointmentStatus.SCHEDULED,
    AppointmentStatus.CONFIRMED,
    AppointmentStatus.RESCHEDULED,
)


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_stats(self) -> dict:
        today = date.today()

        total_patients = (
            await self.session.execute(select(func.count(Patient.id)))
        ).scalar_one()

        total_active_doctors = (
            await self.session.execute(
                select(func.count(Doctor.id)).where(Doctor.status.is_(True))
            )
        ).scalar_one()

        appointments_today = (
            await self.session.execute(
                select(func.count(Appointment.id))
                .join(AppointmentSlot, Appointment.appointment_slot_id == AppointmentSlot.id)
                .where(AppointmentSlot.slot_date == today)
            )
        ).scalar_one()

        upcoming_appointments = (
            await self.session.execute(
                select(func.count(Appointment.id))
                .join(AppointmentSlot, Appointment.appointment_slot_id == AppointmentSlot.id)
                .where(
                    AppointmentSlot.slot_date >= today,
                    Appointment.appointment_status.in_(ACTIVE_STATUSES),
                )
            )
        ).scalar_one()

        ai_calls_today = (
            await self.session.execute(
                select(func.count(CallLog.id)).where(
                    func.date(CallLog.started_at) == today
                )
            )
        ).scalar_one()

        logger.info("get_stats: computed dashboard stats for %s.", today)

        return {
            "total_patients": total_patients,
            "total_active_doctors": total_active_doctors,
            "appointments_today": appointments_today,
            "upcoming_appointments": upcoming_appointments,
            "ai_calls_today": ai_calls_today,
        }

    async def get_appointment_trend(self, days: int = 7) -> list[dict]:
        start_date = date.today() - timedelta(days=days - 1)

        stmt = (
            select(AppointmentSlot.slot_date, func.count(Appointment.id))
            .join(Appointment, Appointment.appointment_slot_id == AppointmentSlot.id)
            .where(AppointmentSlot.slot_date >= start_date)
            .group_by(AppointmentSlot.slot_date)
        )
        result = await self.session.execute(stmt)
        counts_by_date = dict(result.all())

        # Fill in zero-count days so the chart doesn't have gaps.
        return [
            {
                "date": start_date + timedelta(days=offset),
                "count": counts_by_date.get(start_date + timedelta(days=offset), 0),
            }
            for offset in range(days)
        ]

    async def get_department_breakdown(self) -> list[dict]:
        stmt = (
            select(Doctor.department, func.count(Appointment.id))
            .join(Appointment, Appointment.doctor_id == Doctor.id)
            .group_by(Doctor.department)
            .order_by(func.count(Appointment.id).desc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        total = sum(count for _, count in rows) or 1  # avoid div-by-zero on empty DB

        return [
            {
                "department": department,
                "count": count,
                "percentage": round(count / total * 100, 1),
            }
            for department, count in rows
        ]

    async def get_recent_appointments(self, limit: int = 5):
        stmt = (
            select(Appointment, AppointmentSlot, Patient, Doctor)
            .join(AppointmentSlot, Appointment.appointment_slot_id == AppointmentSlot.id)
            .join(Patient, Appointment.patient_id == Patient.id)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .order_by(Appointment.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_recent_calls(self, limit: int = 5):
        stmt = (
            select(CallLog, Patient)
            .outerjoin(Patient, CallLog.patient_id == Patient.id)
            .order_by(CallLog.started_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()