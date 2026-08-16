"""
Service layer for doctor lookups and per-doctor appointment history.
"""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    Appointment,
    AppointmentSlot,
    AppointmentStatus,
    Doctor,
    Patient,
)
from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)


class DoctorService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_doctors(
        self,
        department: Optional[str] = None,
        active_only: bool = True,
    ) -> Sequence[Doctor]:
        stmt = select(Doctor)

        if active_only:
            stmt = stmt.where(Doctor.status.is_(True))
        if department is not None:
            stmt = stmt.where(Doctor.department.ilike(department))

        stmt = stmt.order_by(Doctor.doctor_name)
        result = await self.session.execute(stmt)
        doctors = result.scalars().all()

        logger.info("list_doctors: returned %d doctor(s).", len(doctors))
        return doctors

    async def find_by_id(self, doctor_id: UUID) -> Optional[Doctor]:
        return await self.session.get(Doctor, doctor_id)

    async def get_appointment_history(
        self,
        doctor_id: UUID,
        status_filter: Optional[AppointmentStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ):
        """
        Every appointment ever booked with this doctor, most recent slot
        first, with the patient's name and slot timing joined in — this is
        the query the /doctors/{id}/appointments endpoint needs, since
        AppointmentResponse alone only carries bare IDs.
        """
        stmt = (
            select(Appointment, AppointmentSlot, Patient)
            .join(AppointmentSlot, Appointment.appointment_slot_id == AppointmentSlot.id)
            .join(Patient, Appointment.patient_id == Patient.id)
            .where(Appointment.doctor_id == doctor_id)
        )

        if status_filter is not None:
            stmt = stmt.where(Appointment.appointment_status == status_filter)

        stmt = (
            stmt.order_by(AppointmentSlot.slot_date.desc(), AppointmentSlot.start_time.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        logger.info(
            "get_appointment_history: doctor=%s returned %d row(s).", doctor_id, len(rows)
        )
        return rows