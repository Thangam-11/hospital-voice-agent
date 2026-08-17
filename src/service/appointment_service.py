"""
Service layer — knows the business RULES around booking.
This is what the agent's `book_appointment` tool actually calls.
"""

from datetime import date
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select

from src.database.models import (
    Appointment,
    AppointmentStatus,
    AppointmentSlot,
)
from src.repository.appointment_book import AppointmentSlotRepository
from src.service.activity_logs_service import ActivityLogService
from src.utils.exceptions import (
    SlotNotFoundError,
    SlotUnavailableError,
    AppointmentNotFoundError,
)
from src.utils.logger_exceptions import get_logger

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
        Find available appointment slots.
        """

        return await self.slots.find_available(
            specialization=specialization,
            date_from=date_from,
            limit=limit,
        )

    async def book_appointment(
        self,
        patient_id: UUID,
        slot_id: UUID,
        reason: Optional[str] = None,
    ) -> Appointment:
        """
        Book an appointment and create an activity log.
        """

        logger.info(
            "book_appointment: patient=%s slot=%s reason=%r",
            patient_id,
            slot_id,
            reason,
        )

        # Lock the slot so two requests cannot book it simultaneously.
        slot = await self.slots.get_for_update(slot_id)

        if slot is None:
            logger.warning(
                "book_appointment: slot %s not found.",
                slot_id,
            )

            raise SlotNotFoundError(
                f"No slot found with id {slot_id}."
            )

        if not slot.is_available:
            logger.warning(
                "book_appointment: slot %s already booked.",
                slot_id,
            )

            raise SlotUnavailableError(
                "That slot has already been booked."
            )

        # Mark slot unavailable.
        slot.is_available = False

        # Create appointment.
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=slot.doctor_id,
            appointment_slot_id=slot.id,
            appointment_status=AppointmentStatus.SCHEDULED,
            booking_reason=reason,
        )

        self.session.add(appointment)

        # Generate appointment.id before creating activity log.
        await self.session.flush()

        # Create application-wide activity history.
        await ActivityLogService.log(
            self.session,
            event_type="APPOINTMENT_BOOKED",
            entity_type="appointment",
            entity_id=appointment.id,
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            actor_type="SYSTEM",
            description="Appointment booked successfully",
            metadata={
                "doctor_id": str(appointment.doctor_id),
                "slot_id": str(appointment.appointment_slot_id),
                "reason": reason,
            },
        )

        # Commit appointment + slot update + activity log.
        await self.session.commit()

        logger.info(
            "book_appointment: booked appointment=%s "
            "for patient=%s with doctor=%s.",
            appointment.id,
            patient_id,
            slot.doctor_id,
        )

        return appointment

async def cancel_appointment(
    self,
    appointment_id: UUID,
    patient_id: UUID,
) -> Appointment:
    """
    Cancels an appointment — only if it belongs to the requesting patient.

    This ownership check is what the voice agent's identity
    verification depends on.
    """

    logger.info(
        "cancel_appointment: appointment=%s patient=%s",
        appointment_id,
        patient_id,
    )

    appointment = await self.session.get(
        Appointment,
        appointment_id,
    )

    if appointment is None or appointment.patient_id != patient_id:
        logger.warning(
            "cancel_appointment: no appointment %s "
            "found for patient %s.",
            appointment_id,
            patient_id,
        )

        raise AppointmentNotFoundError(
            f"No appointment found with id {appointment_id}."
        )

    # Idempotent cancellation.
    if appointment.appointment_status == AppointmentStatus.CANCELLED:
        logger.info(
            "cancel_appointment: appointment %s already cancelled.",
            appointment_id,
        )

        return appointment

    # Update appointment status.
    appointment.appointment_status = AppointmentStatus.CANCELLED

    # Make the slot available again.
    slot = await self.slots.get_for_update(
        appointment.appointment_slot_id
    )

    if slot is not None:
        slot.is_available = True

    # Record cancellation in activity history.
    await ActivityLogService.log(
        self.session,
        event_type="APPOINTMENT_CANCELLED",
        entity_type="appointment",
        entity_id=appointment.id,
        patient_id=appointment.patient_id,
        appointment_id=appointment.id,
        actor_type="SYSTEM",
        description="Appointment cancelled successfully",
        metadata={
            "doctor_id": str(appointment.doctor_id),
            "slot_id": str(appointment.appointment_slot_id),
        },
    )

    # Commit appointment + slot + activity log together.
    await self.session.commit()

    logger.info(
        "cancel_appointment: cancelled appointment=%s.",
        appointment_id,
    )

    return appointment
    async def check_status(
        self,
        patient_id: UUID,
    ) -> Sequence[Appointment]:
        """
        Returns all appointments for a patient,
        most recent first.
        """

        stmt = (
            select(Appointment)
            .join(
                AppointmentSlot,
                Appointment.appointment_slot_id
                == AppointmentSlot.id,
            )
            .where(
                Appointment.patient_id == patient_id
            )
            .order_by(
                AppointmentSlot.slot_date.desc(),
                AppointmentSlot.start_time.desc(),
            )
        )

        result = await self.session.execute(stmt)

        appointments = result.scalars().all()

        logger.info(
            "check_status: found %d appointment(s) "
            "for patient=%s.",
            len(appointments),
            patient_id,
        )

        return appointments