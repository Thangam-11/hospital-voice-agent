"""
Service layer for patient lookups.
"""

from datetime import date
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Patient
from src.utils.logger_exceptions import get_logger

logger = get_logger(__name__)


class PatientService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_name_and_dob(
        self, full_name: str, date_of_birth: date
    ) -> Optional[Patient]:
        normalized_name = " ".join(full_name.strip().split())

        stmt = select(Patient).where(
            func.lower(func.trim(Patient.full_name)) == normalized_name.lower(),
            Patient.date_of_birth == date_of_birth,
        )
        result = await self.session.execute(stmt)
        matches = result.scalars().all()

        if len(matches) == 0:
            logger.info("No patient match for provided name/DOB.")
            return None
        if len(matches) > 1:
            logger.warning(
                "Ambiguous patient match: %d records for name/DOB. Refusing to disambiguate.",
                len(matches),
            )
            return None
        return matches[0]

    async def find_by_id(self, patient_id: UUID) -> Optional[Patient]:
        stmt = select(Patient).where(Patient.id == patient_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_patients(
        self, limit: int = 20, offset: int = 0
    ) -> Sequence[Patient]:
        """
        Returns patients ordered by creation time, most recent first.
        Testing/admin use only — see router-level warning about this
        endpoint's lack of auth before exposing it anywhere non-local.
        """
        stmt = (
            select(Patient)
            .order_by(Patient.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        patients = result.scalars().all()
        logger.info("list_patients: returned %d patient(s).", len(patients))
        return patients