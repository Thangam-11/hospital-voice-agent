# src/agent/tools.py

from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from src.service.appointment_service import AppointmentService
from src.service.patient_service import PatientService
from src.utils.logger_exceptions import get_logger


logger = get_logger(__name__)


def create_appointment_tools(
    service: AppointmentService,
    patient_service: PatientService,
):

    # ============================================================
    # RESPONSE TOOL
    # ============================================================

    @tool
    async def respond_to_patient(
        message: str,
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        Send a natural-language response to the patient.

        Use this when no database action is required or after a
        successful tool operation.
        """

        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=message,
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # ============================================================
    # VERIFY PATIENT
    # ============================================================

    @tool
    async def verify_patient(
        full_name: str,
        date_of_birth: date,
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        Verify a patient using the full name and date of birth
        explicitly provided by the patient.

        Maximum two verification attempts.
        """

        attempts = state.get("verification_attempts", 0)

        if attempts >= 2:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=(
                                "Maximum verification attempts reached. "
                                "Do not call verify_patient again. "
                                "Tell the patient you are transferring "
                                "them to hospital staff."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        try:
            patient = await patient_service.find_by_name_and_dob(
                full_name=full_name,
                date_of_birth=date_of_birth,
            )

        except Exception:
            logger.exception("verify_patient failed")

            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=(
                                "Patient verification is temporarily "
                                "unavailable. Please try again later."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        if patient is None:
            return Command(
                update={
                    "verification_attempts": attempts + 1,
                    "messages": [
                        ToolMessage(
                            content=(
                                "No matching patient record was found. "
                                "Ask the patient to repeat their full "
                                "name and date of birth."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )

        return Command(
            update={
                "patient_id": patient.id,
                "verification_attempts": 0,
                "messages": [
                    ToolMessage(
                        content=(
                            f"Patient verification successful. "
                            f"Patient name: {patient.full_name}."
                        ),
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    # ============================================================
    # FIND AVAILABLE SLOTS
    # ============================================================

    @tool
    async def find_available_slots(
        specialization: Optional[str] = None,
        date_from: Optional[date] = None,
        limit: int = 10,
        tool_call_id: Annotated[str, InjectedToolCallId] = "",
    ) -> Command:
        """
        Find available hospital appointment slots.

        This does not require patient verification.

        specialization must be a plain string such as:
        "Cardiology" or "Cardiologist".
        """

        # Defensive normalization: some OpenRouter providers serving
        # this model occasionally wrap scalar values in a
        # {"type": "string", "value": "..."} envelope instead of
        # passing them directly. Normalize here rather than sending
        # that shape into the service layer.
        if isinstance(specialization, dict):
            specialization = specialization.get("value")

        if specialization is not None:
            specialization = specialization.strip()

        logger.info(
            "find_available_slots: specialization=%r date_from=%r limit=%s",
            specialization,
            date_from,
            limit,
        )

        try:
            slots = await service.find_available_slots(
                specialization=specialization,
                date_from=date_from,
                limit=limit,
            )

        except Exception:
            logger.exception("find_available_slots failed")

            return Command(
                update={
                    "intent": "find_slots",
                    "messages": [
                        ToolMessage(
                            content=(
                                "I couldn't retrieve appointment "
                                "availability right now."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )

        if not slots:
            return Command(
                update={
                    "intent": "find_slots",
                    "specialization": specialization,
                    "date_from": str(date_from) if date_from else None,
                    "messages": [
                        ToolMessage(
                            content=(
                                "No available appointment slots "
                                "were found for the requested criteria."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )

        slot_summaries = []

        for slot in slots:
            slot_summaries.append(
                {
                    "slot_id": str(slot.id),
                    "doctor_id": str(slot.doctor_id),
                    "date": str(slot.slot_date),
                    "start_time": str(slot.start_time),
                    "end_time": str(slot.end_time),
                }
            )

        return Command(
            update={
                "intent": "find_slots",
                "specialization": specialization,
                "date_from": str(date_from) if date_from else None,
                "messages": [
                    ToolMessage(
                        content=str(slot_summaries),
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    # ============================================================
    # CONFIRM SLOT SELECTION
    # ============================================================
    #
    # book_appointment checks state["slot_confirmed"] AND that it
    # matches the exact slot_id being booked — this is the ONLY tool
    # that should set those, and only after the patient has verbally
    # confirmed a specific slot read back to them by the agent.
    # ============================================================

    @tool
    async def confirm_slot_selection(
        slot_id: UUID,
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        Record that the patient has explicitly confirmed a specific
        appointment slot out loud.

        Call this ONLY after the patient has clearly agreed to a
        specific date/time/doctor you read back to them — not merely
        because they mentioned a preference. After calling this,
        proceed to book_appointment with the same slot_id.
        """

        return Command(
            update={
                "selected_slot_id": slot_id,
                "slot_confirmed": True,
                "messages": [
                    ToolMessage(
                        content=(
                            "Slot selection confirmed. You may now "
                            "call book_appointment with this slot_id."
                        ),
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    # ============================================================
    # BOOK APPOINTMENT
    # ============================================================

    @tool
    async def book_appointment(
        slot_id: UUID,
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
        reason: Optional[str] = None,
    ) -> Command:
        """
        Book an appointment for the verified patient.

        confirm_slot_selection must have been called for this exact
        slot_id first.
        """

        patient_id = state.get("patient_id")

        if patient_id is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=(
                                "Patient identity has not been verified. "
                                "Verify the patient before booking."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        slot_confirmed = state.get("slot_confirmed", False)
        confirmed_slot_id = state.get("selected_slot_id")

        if not slot_confirmed or confirmed_slot_id != slot_id:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=(
                                "This slot has not been explicitly "
                                "confirmed by the patient. Read the "
                                "slot back to them, get a clear yes, "
                                "then call confirm_slot_selection "
                                "before booking."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        try:
            appointment = await service.book_appointment(
                patient_id=patient_id,
                slot_id=slot_id,
                reason=reason,
            )

        except Exception:
            logger.exception("book_appointment failed")

            return Command(
                update={
                    "intent": "book_appointment",
                    "slot_confirmed": False,
                    "selected_slot_id": None,
                    "messages": [
                        ToolMessage(
                            content=(
                                "The appointment could not be booked. "
                                "The slot may no longer be available."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )

        return Command(
            update={
                "intent": "book_appointment",
                "selected_slot_id": slot_id,
                "appointment_id": appointment.id,
                "slot_confirmed": False,
                "messages": [
                    ToolMessage(
                        content=(
                            "Appointment successfully booked. "
                            f"Status: {appointment.appointment_status.value}."
                        ),
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    # ============================================================
    # CONFIRM CANCELLATION
    # ============================================================
    #
    # Uses a SEPARATE field (confirmed_cancellation_id) from
    # appointment_id, which book_appointment also writes to (the ID
    # of a just-booked appointment) — reusing the same key would let
    # one silently overwrite the other mid-conversation.
    # ============================================================

    @tool
    async def confirm_cancellation(
        appointment_id: UUID,
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        Record that the patient has explicitly confirmed they want to
        cancel a specific appointment out loud.

        Call this ONLY after the patient has clearly agreed to cancel
        the specific appointment you read back to them. After calling
        this, proceed to cancel_appointment with the same
        appointment_id.
        """

        return Command(
            update={
                "confirmed_cancellation_id": appointment_id,
                "cancellation_confirmed": True,
                "messages": [
                    ToolMessage(
                        content=(
                            "Cancellation confirmed. You may now call "
                            "cancel_appointment with this appointment_id."
                        ),
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    # ============================================================
    # CANCEL APPOINTMENT
    # ============================================================

    @tool
    async def cancel_appointment(
        appointment_id: UUID,
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        Cancel an existing appointment belonging to the verified
        patient.

        confirm_cancellation must have been called for this exact
        appointment_id first.
        """

        patient_id = state.get("patient_id")

        if patient_id is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=(
                                "Patient identity has not been verified. "
                                "Verify the patient before cancelling."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        cancellation_confirmed = state.get("cancellation_confirmed", False)
        confirmed_appointment_id = state.get("confirmed_cancellation_id")

        if not cancellation_confirmed or confirmed_appointment_id != appointment_id:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=(
                                "This cancellation has not been "
                                "explicitly confirmed by the patient. "
                                "Read the appointment back to them, get "
                                "a clear yes, then call "
                                "confirm_cancellation before cancelling."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        try:
            await service.cancel_appointment(
                appointment_id=appointment_id,
                patient_id=patient_id,
            )

        except Exception:
            logger.exception("cancel_appointment failed")

            return Command(
                update={
                    "intent": "cancel_appointment",
                    "cancellation_confirmed": False,
                    "confirmed_cancellation_id": None,
                    "messages": [
                        ToolMessage(
                            content=(
                                "I couldn't cancel that appointment. "
                                "It may not exist or may not belong "
                                "to this patient."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )

        return Command(
            update={
                "intent": "cancel_appointment",
                "cancellation_confirmed": False,
                "confirmed_cancellation_id": None,
                "messages": [
                    ToolMessage(
                        content="The appointment was successfully cancelled.",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    # ============================================================
    # CHECK APPOINTMENT STATUS
    # ============================================================

    @tool
    async def check_appointment_status(
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        Check the verified patient's appointments.
        """

        patient_id = state.get("patient_id")

        if patient_id is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=(
                                "Patient identity has not been verified. "
                                "Verify the patient before checking "
                                "appointment status."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        try:
            appointments = await service.check_status(patient_id)

        except Exception:
            logger.exception("check_appointment_status failed")

            return Command(
                update={
                    "intent": "check_status",
                    "messages": [
                        ToolMessage(
                            content=(
                                "I couldn't retrieve the appointment "
                                "information right now."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )

        if not appointments:
            return Command(
                update={
                    "intent": "check_status",
                    "messages": [
                        ToolMessage(
                            content=(
                                "There are no upcoming appointments "
                                "for this patient."
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )

        summaries = []

        for appointment in appointments:
            summaries.append(
                {
                    "appointment_id": str(appointment.id),
                    "doctor_id": str(appointment.doctor_id),
                    "slot_id": str(appointment.appointment_slot_id),
                    "status": appointment.appointment_status.value,
                }
            )

        return Command(
            update={
                "intent": "check_status",
                "messages": [
                    ToolMessage(
                        content=str(summaries),
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    return [
        respond_to_patient,
        verify_patient,
        find_available_slots,
        confirm_slot_selection,
        book_appointment,
        confirm_cancellation,
        cancel_appointment,
        check_appointment_status,
    ]