from datetime import date
from typing import Optional
from uuid import UUID

from langchain_core.tools import tool

from src.service.appointment_service import AppointmentService


def create_appointment_tools(service: AppointmentService):

    @tool
    async def find_available_slots(
        specialization: Optional[str] = None,
        date_from: Optional[date] = None,
        limit: int = 10,
    ):
        """
        Find available hospital appointment slots.

        Use this when the patient wants to:
        - find a doctor
        - find available appointments
        - check available times
        """

        slots = await service.find_available_slots(
            specialization=specialization,
            date_from=date_from,
            limit=limit,
        )

        return [
            {
                "slot_id": str(slot.id),
                "doctor_id": str(slot.doctor_id),
                "date": str(slot.slot_date),
                "start_time": str(slot.start_time),
                "end_time": str(slot.end_time),
            }
            for slot in slots
        ]

    @tool
    async def book_appointment(
        patient_id: UUID,
        slot_id: UUID,
        reason: Optional[str] = None,
    ):
        """
        Book an appointment for a patient.

        Use this only after the patient has selected
        a specific appointment slot.
        """

        appointment = await service.book_appointment(
            patient_id=patient_id,
            slot_id=slot_id,
            reason=reason,
        )

        return {
            "success": True,
            "appointment_id": str(appointment.id),
            "patient_id": str(appointment.patient_id),
            "doctor_id": str(appointment.doctor_id),
            "slot_id": str(appointment.appointment_slot_id),
            "status": appointment.appointment_status.value,
        }

    @tool
    async def cancel_appointment(
        appointment_id: UUID,
    ):
        """
        Cancel an existing appointment.
        """

        appointment = await service.cancel_appointment(
            appointment_id=appointment_id
        )

        return {
            "success": True,
            "appointment_id": str(appointment.id),
            "status": appointment.appointment_status.value,
        }

    @tool
    async def check_appointment_status(
        patient_id: UUID,
    ):
        """
        Check a patient's appointments and their status.
        """

        appointments = await service.check_status(
            patient_id
        )

        return [
            {
                "appointment_id": str(appointment.id),
                "doctor_id": str(appointment.doctor_id),
                "slot_id": str(appointment.appointment_slot_id),
                "status": appointment.appointment_status.value,
            }
            for appointment in appointments
        ]

    return [
        find_available_slots,
        book_appointment,
        cancel_appointment,
        check_appointment_status,
    ]