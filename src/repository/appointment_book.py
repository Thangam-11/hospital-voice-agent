"""
Repository layer — knows HOW to fetch/persist data. No business rules here,
just queries.
"""

from datetime import date
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select

from src.database.models import AppointmentSlot, Doctor
from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)


class AppointmentSlotRepository:
    def __init__(self, session):
        self.session = session
        logger.debug("AppointmentSlotRepository instantiated.")

    async def find_available(
        self,
        specialization: Optional[str] = None,
        date_from: Optional[date] = None,
        limit: int = 10,
    ) -> Sequence[AppointmentSlot]:
        """Find open slots, optionally filtered by doctor specialization and date."""
        stmt = select(AppointmentSlot).where(AppointmentSlot.is_available.is_(True))

        if specialization is not None:
            stmt = stmt.join(Doctor, AppointmentSlot.doctor_id == Doctor.id).where(
                Doctor.specialization.ilike(specialization)
            )
        if date_from is not None:
            stmt = stmt.where(AppointmentSlot.slot_date >= date_from)

        stmt = stmt.order_by(AppointmentSlot.slot_date, AppointmentSlot.start_time).limit(limit)
        result = await self.session.execute(stmt)
        slots = result.scalars().all()

        logger.info(
            "find_available returned %d slot(s) (specialization=%s, date_from=%s).",
            len(slots), specialization, date_from,
        )
        return slots

    async def get_for_update(self, slot_id: UUID) -> Optional[AppointmentSlot]:
        """
        Locks the row (SELECT ... FOR UPDATE) so two callers can't both book
        the same slot at the same time. On Postgres, the second transaction
        blocks here until the first one commits or rolls back.
        """
        stmt = select(AppointmentSlot).where(AppointmentSlot.id == slot_id).with_for_update()
        result = await self.session.execute(stmt)
        slot = result.scalar_one_or_none()

        if slot is None:
            logger.warning("get_for_update: no slot found for id %s.", slot_id)
        else:
            logger.info("get_for_update: locked slot %s (is_available=%s).", slot_id, slot.is_available)

        return slot