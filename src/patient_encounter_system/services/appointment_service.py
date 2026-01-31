from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from src.patient_encounter_system.models.appointment import Appointment
from src.patient_encounter_system.models.doctor import Doctor


def create_appointment(db: Session, data):
    if data.start_time.tzinfo is None:
        raise HTTPException(400, "Datetime must be timezone-aware")

    if data.start_time <= datetime.now(timezone.utc):
        raise HTTPException(400, "Appointment must be in the future")

    doctor = db.get(Doctor, data.doctor_id)
    if not doctor or not doctor.active:  # fixed: use .active
        raise HTTPException(400, "Doctor inactive or not found")

    end_time = data.start_time + timedelta(minutes=data.duration_minutes)

    # ✅ fixed overlap check
    existing_appts = (
        db.query(Appointment).filter(Appointment.doctor_id == data.doctor_id).all()
    )
    for existing in existing_appts:
        existing_start = existing.start_time
        if existing_start.tzinfo is None:
            existing_start = existing_start.replace(tzinfo=timezone.utc)
        existing_end = existing_start + timedelta(minutes=existing.duration_minutes)
        if existing_start < end_time and existing_end > data.start_time:
            raise HTTPException(409, "Doctor has overlapping appointment")

    appt = Appointment(**data.model_dump())  # use model_dump instead of dict
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt
