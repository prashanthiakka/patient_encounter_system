from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from src.patient_encounter_system.database import Base, engine, SessionLocal
from src.patient_encounter_system.models.patient import Patient
from src.patient_encounter_system.models.doctor import Doctor
from src.patient_encounter_system.models.appointment import Appointment
from src.patient_encounter_system.schemas.patient import PatientCreate, PatientRead
from src.patient_encounter_system.schemas.doctor import DoctorCreate, DoctorRead
from src.patient_encounter_system.schemas.appointment import (
    AppointmentCreate,
    AppointmentRead,
)

# ✅ Only create tables if they don’t exist — don’t drop them
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Encounter Management System")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- PATIENT ENDPOINTS ----------------
@app.post("/patients", response_model=PatientRead, status_code=201)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    existing = db.query(Patient).filter(Patient.email == patient.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    db_patient = Patient(**patient.model_dump())  # ✅ use model_dump for Pydantic v2
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.get("/patients/{patient_id}", response_model=PatientRead)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# ---------------- DOCTOR ENDPOINTS ----------------
@app.post("/doctors", response_model=DoctorRead, status_code=201)
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    db_doctor = Doctor(**doctor.model_dump())  # ✅ use model_dump
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


@app.get("/doctors/{doctor_id}", response_model=DoctorRead)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


# ---------------- APPOINTMENT ENDPOINTS ----------------
@app.post("/appointments", response_model=AppointmentRead, status_code=201)
def create_appointment(appt: AppointmentCreate, db: Session = Depends(get_db)):
    if appt.start_time <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400, detail="Appointment must be scheduled in the future"
        )

    if appt.duration_minutes < 15 or appt.duration_minutes > 180:
        raise HTTPException(
            status_code=400, detail="Duration must be between 15 and 180 minutes"
        )

    doctor = db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
    if not doctor or not doctor.active:
        raise HTTPException(status_code=400, detail="Doctor not available")

    new_end = appt.start_time + timedelta(minutes=appt.duration_minutes)
    existing_appts = (
        db.query(Appointment).filter(Appointment.doctor_id == appt.doctor_id).all()
    )

    for existing in existing_appts:
        existing_start = existing.start_time
        if existing_start.tzinfo is None:
            existing_start = existing_start.replace(tzinfo=timezone.utc)
        existing_end = existing_start + timedelta(minutes=existing.duration_minutes)
        if existing_start < new_end and existing_end > appt.start_time:
            raise HTTPException(
                status_code=409, detail="Doctor already has an overlapping appointment"
            )

    db_appt = Appointment(**appt.model_dump())  # ✅ use model_dump
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    return db_appt


@app.get("/appointments", response_model=list[AppointmentRead])
def list_appointments(
    date: str, doctor_id: int | None = None, db: Session = Depends(get_db)
):
    try:
        query_date = datetime.fromisoformat(date).date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format, use YYYY-MM-DD"
        )

    start_of_day = datetime.combine(
        query_date, datetime.min.time(), tzinfo=timezone.utc
    )
    end_of_day = start_of_day + timedelta(days=1)

    q = db.query(Appointment).filter(
        Appointment.start_time >= start_of_day, Appointment.start_time < end_of_day
    )
    if doctor_id:
        q = q.filter(Appointment.doctor_id == doctor_id)

    return q.all()
