"""
Patient router. Read-only for now — creating/editing patients isn't in
scope yet, this exists to support testing and to pair with the voice
agent's verify_patient flow.

⚠️ No authentication here. Returns real patient PII (name, DOB, phone,
email) to anyone who can reach this endpoint. Fine for local dev against
localhost; do NOT expose this router as-is on any shared or public
deployment without adding auth first.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_engine import get_db
from src.service.patient_service import PatientService
from src.api_service.schemas.patient_schema import PatientResponse, PatientListResponse

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=PatientListResponse)
async def list_patients(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    service = PatientService(session)
    patients = await service.list_patients(limit=limit, offset=offset)
    return PatientListResponse(patients=patients, count=len(patients))


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    service = PatientService(session)
    patient = await service.find_by_id(patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    return patient