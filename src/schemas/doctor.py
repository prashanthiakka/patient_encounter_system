from pydantic import BaseModel
from datetime import datetime


class DoctorCreate(BaseModel):
    full_name: str
    specialization: str
    active: bool = True


class DoctorRead(DoctorCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
