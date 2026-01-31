from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.patient_encounter_system.models.doctor import Doctor
from src.patient_encounter_system.models.appointment import Appointment


def create_doctor(db: Session, data):
    doctor = Doctor(**data.dict())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def get_doctor(db: Session, doctor_id: int):
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(404, "Doctor not found")
    return doctor


def deactivate_doctor(db: Session, doctor_id: int):
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(404, "Doctor not found")

    doctor.active = False
    db.commit()
    db.refresh(doctor)
    return doctor


def delete_doctor(db: Session, doctor_id: int):
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(404, "Doctor not found")

    # Rule: Doctors with appointments must not be deleted
    has_appts = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).first()
    if has_appts:
        raise HTTPException(400, "Cannot delete doctor with existing appointments")

    db.delete(doctor)
    db.commit()
    return {"detail": "Doctor deleted"}
