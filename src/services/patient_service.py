from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.patient import Patient
from src.models.appointment import Appointment


def create_patient(db: Session, data):
    # Enforce unique email
    existing = db.query(Patient).filter(Patient.email == data.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")

    patient = Patient(**data.dict())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient


def delete_patient(db: Session, patient_id: int):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    # Rule: Patients with appointments must not be deleted
    has_appts = (
        db.query(Appointment).filter(Appointment.patient_id == patient_id).first()
    )
    if has_appts:
        raise HTTPException(400, "Cannot delete patient with existing appointments")

    db.delete(patient)
    db.commit()
    return {"detail": "Patient deleted"}
