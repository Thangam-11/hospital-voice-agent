from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_engine import get_db
from src.database.models import ActivityLog


router = APIRouter(
    prefix="/activity-logs",
    tags=["activity-logs"],
)


@router.get("")
async def get_activity_logs(
    limit: int = Query(default=20, ge=1, le=100),
    patient_id: UUID | None = None,
    appointment_id: UUID | None = None,
    session: AsyncSession = Depends(get_db),
):
    stmt = (
        select(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    )

    if patient_id:
        stmt = stmt.where(ActivityLog.patient_id == patient_id)

    if appointment_id:
        stmt = stmt.where(
            ActivityLog.appointment_id == appointment_id
        )

    result = await session.execute(stmt)

    return result.scalars().all()