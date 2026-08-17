from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import ActivityLog


class ActivityLogService:
    """Service for recording application-wide activity history."""

    @staticmethod
    async def log(
        db: AsyncSession,
        *,
        event_type: str,
        entity_type: str,
        actor_type: str,
        entity_id: UUID | None = None,
        patient_id: UUID | None = None,
        appointment_id: UUID | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ActivityLog:
        """
        Create an activity log entry.

        Example:
            await ActivityLogService.log(
                db,
                event_type="APPOINTMENT_BOOKED",
                entity_type="appointment",
                entity_id=appointment.id,
                patient_id=appointment.patient_id,
                appointment_id=appointment.id,
                actor_type="AI_AGENT",
                description="Appointment booked successfully",
                metadata={
                    "doctor_id": str(appointment.doctor_id),
                    "slot_id": str(appointment.appointment_slot_id),
                },
            )
        """

        activity = ActivityLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            patient_id=patient_id,
            appointment_id=appointment_id,
            actor_type=actor_type,
            description=description,
            log_metadata=metadata,
        )

        db.add(activity)

        # Flush so the record is sent to PostgreSQL immediately
        # while keeping the transaction controlled by the caller.
        await db.flush()

        return activity