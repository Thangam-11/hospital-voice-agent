"""
Service layer — knows the business RULES around booking. This is what the
agent's `book_appointment` tool actually calls.
"""

from datetime import date
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select

from src.database.models import Appointment, AppointmentStatus, AppointmentSlot
from src.repository.appointment_book import AppointmentSlotRepository
from src.utils.logger_exceptions import get_logger
from src.utils.exceptions import (
    SlotNotFoundError,
    SlotUnavailableError,
    AppointmentNotFoundError,
)

logger = get_logger(__name__)


class AppointmentService:
    def __init__(self, session):
        self.session = session
        self.slots = AppointmentSlotRepository(session)
        logger.debug("AppointmentService instantiated.")

    async def find_available_slots(
        self,
        specialization: Optional[str] = None,
        date_from: Optional[date] = None,
        limit: int = 10,
    ) -> Sequence[AppointmentSlot]:
        """
        Thin pass-through to the repository — no business rules needed here,
        finding availability doesn't touch booking state.
        """
        return await self.slots.find_available(
            specialization=specialization, date_from=date_from, limit=limit
        )

    async def book_appointment(
        self, patient_id: UUID, slot_id: UUID, reason: Optional[str] = None
    ) -> Appointment:
        logger.info("book_appointment: patient=%s slot=%s reason=%r", patient_id, slot_id, reason)

        slot = await self.slots.get_for_update(slot_id)

        if slot is None:
            logger.warning("book_appointment: slot %s not found.", slot_id)
            raise SlotNotFoundError(f"No slot found with id {slot_id}.")

        if not slot.is_available:
            logger.warning("book_appointment: slot %s already booked.", slot_id)
            raise SlotUnavailableError("That slot has already been booked.")

        slot.is_available = False

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=slot.doctor_id,
            appointment_slot_id=slot.id,
            appointment_status=AppointmentStatus.SCHEDULED,
            booking_reason=reason,
        )
        self.session.add(appointment)
        await self.session.commit()

        logger.info(
            "book_appointment: booked appointment=%s for patient=%s with doctor=%s.",
            appointment.id, patient_id, slot.doctor_id,
        )
        return appointment

    async def cancel_appointment(self, appointment_id: UUID, patient_id: UUID) -> Appointment:
        """
        Cancels an appointment — only if it belongs to the requesting patient.
        This ownership check is what the voice agent's identity verification
        depends on: without it, any verified patient could cancel any
        appointment_id they happened to guess.
        """
        logger.info("cancel_appointment: appointment=%s patient=%s", appointment_id, patient_id)

        appointment = await self.session.get(Appointment, appointment_id)

        if appointment is None or appointment.patient_id != patient_id:
            # Same error either way — don't reveal that the ID exists but
            # belongs to someone else.
            logger.warning(
                "cancel_appointment: no appointment %s found for patient %s.",
                appointment_id, patient_id,
            )
            raise AppointmentNotFoundError(f"No appointment found with id {appointment_id}.")

        if appointment.appointment_status == AppointmentStatus.CANCELLED:
            logger.info("cancel_appointment: appointment %s already cancelled.", appointment_id)
            return appointment  # idempotent

        appointment.appointment_status = AppointmentStatus.CANCELLED

        slot = await self.slots.get_for_update(appointment.appointment_slot_id)
        if slot is not None:
            slot.is_available = True

        await self.session.commit()

        logger.info("cancel_appointment: cancelled appointment=%s.", appointment_id)
        return appointment

    async def check_status(self, patient_id: UUID) -> Sequence[Appointment]:
        """
        Returns all appointments for a patient, most recent first.

        No dedicated repository for this yet — querying Appointment directly
        via the session. If appointment lookups grow more complex (filtering
        by status, date range, doctor), pull this into an
        AppointmentRepository to keep the service free of raw SQLAlchemy.
        """
        stmt = (
            select(Appointment)
            .join(AppointmentSlot, Appointment.appointment_slot_id == AppointmentSlot.id)
            .where(Appointment.patient_id == patient_id)
            .order_by(AppointmentSlot.slot_date.desc(), AppointmentSlot.start_time.desc())
        )
        result = await self.session.execute(stmt)
        appointments = result.scalars().all()

        logger.info("check_status: found %d appointment(s) for patient=%s.", len(appointments), patient_id)
        return appointments