from pydantic import BaseModel, EmailStr
from datetime import datetime


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str


class PatientRead(PatientCreate):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True
