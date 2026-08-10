"""
Service layer — knows the business RULES around booking. This is what the
agent's `book_appointment` tool actually calls.
"""

from typing import Optional
from uuid import UUID

from src.database.models import Appointment, AppointmentStatus
from src.repository.appointment_book import AppointmentSlotRepository
from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)


class SlotNotFoundError(Exception):
    pass


class SlotUnavailableError(Exception):
    pass


class AppointmentService:
    def __init__(self, session):
        self.session = session
        self.slots = AppointmentSlotRepository(session)
        logger.debug("AppointmentService instantiated.")

    async def book_appointment(
        self, patient_id: UUID, slot_id: UUID, reason: Optional[str] = None
    ) -> Appointment:
        """
        Books a patient into a doctor's slot.

        Business rules enforced here (not in the repository):
        1. The slot must exist.
        2. The slot must currently be available.
        3. Booking + marking the slot unavailable happen in the SAME
           transaction, so a crash between the two steps can't leave the
           slot open while an appointment already claims it.
        """
        logger.info("book_appointment: patient=%s slot=%s reason=%r", patient_id, slot_id, reason)

        slot = await self.slots.get_for_update(slot_id)

        if slot is None:
            logger.warning("book_appointment: slot %s not found.", slot_id)
            raise SlotNotFoundError(f"No slot found with id {slot_id}.")

        if not slot.is_available:
            logger.warning("book_appointment: slot %s already booked.", slot_id)
            raise SlotUnavailableError("That slot has already been booked.")

        # Rule: booking a slot always marks it unavailable, atomically.
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