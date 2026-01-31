from pydantic import BaseModel, validator
from datetime import datetime


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int

    @validator("duration_minutes")
    def duration_bounds(cls, v):
        if v < 15 or v > 180:
            raise ValueError("Duration must be between 15 and 180 minutes")
        return v


class AppointmentRead(AppointmentCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
