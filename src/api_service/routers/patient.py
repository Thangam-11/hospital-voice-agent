"""
Patient router.

Supports patient lookup, listing, and registration.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_service.schemas.patient_schema import (
    PatientCreateRequest,
    PatientListResponse,
    PatientResponse,
)
from src.database.base_engine import get_db
from src.service.patient_service import PatientService

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_patient(
    payload: PatientCreateRequest,
    session: AsyncSession = Depends(get_db),
):
    service = PatientService(session)

    patient = await service.register_patient(
        full_name=payload.full_name,
        gender=payload.gender,
        date_of_birth=payload.date_of_birth,
        phone_number=payload.phone_number,
        email=str(payload.email) if payload.email else None,
        actor_type="SYSTEM",
        registration_source="hospital_system",
    )

    return patient


@router.get(
    "",
    response_model=PatientListResponse,
)
async def list_patients(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    service = PatientService(session)

    patients = await service.list_patients(
        limit=limit,
        offset=offset,
    )

    return PatientListResponse(
        patients=patients,
        count=len(patients),
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
async def get_patient(
    patient_id: UUID,
    session: AsyncSession = Depends(get_db),
):
    service = PatientService(session)

    patient = await service.find_by_id(patient_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    return patient