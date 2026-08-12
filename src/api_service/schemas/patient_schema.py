from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    date_of_birth: date
    phone_number: str
    gender: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None


class PatientListResponse(BaseModel):
    patients: list[PatientResponse]
    count: int