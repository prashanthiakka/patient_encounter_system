import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

from src.patient_encounter_system.main import app
from src.patient_encounter_system.database import Base, engine, SessionLocal
from src.patient_encounter_system.services import (
    appointment_service,
    patient_service,
    doctor_service,
)
from src.patient_encounter_system.schemas.patient import PatientCreate
from src.patient_encounter_system.schemas.doctor import DoctorCreate
from src.patient_encounter_system.schemas.appointment import AppointmentCreate

# Reset DB before API tests
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ---------------- API TESTS ----------------
def test_create_and_get_patient():
    resp = client.post(
        "/patients",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "1234567890",
        },
    )
    assert resp.status_code == 201
    patient_id = resp.json()["id"]

    get_resp = client.get(f"/patients/{patient_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == "john@example.com"


def test_duplicate_patient_email():
    resp = client.post(
        "/patients",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "john@example.com",  # duplicate
            "phone": "5555555555",
        },
    )
    assert resp.status_code == 400


def test_get_nonexistent_patient():
    resp = client.get("/patients/9999")
    assert resp.status_code == 404


def test_create_and_get_doctor():
    resp = client.post(
        "/doctors",
        json={
            "full_name": "Dr. Strange",
            "specialization": "Magic",
            "active": True,
        },
    )
    assert resp.status_code == 201
    doctor_id = resp.json()["id"]

    get_resp = client.get(f"/doctors/{doctor_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["specialization"] == "Magic"


def test_get_nonexistent_doctor():
    resp = client.get("/doctors/9999")
    assert resp.status_code == 404


def test_create_valid_appointment():
    patient = client.post(
        "/patients",
        json={
            "first_name": "Alice",
            "last_name": "Wonder",
            "email": "alice@example.com",
            "phone": "5551234567",
        },
    ).json()
    doctor = client.post(
        "/doctors",
        json={
            "full_name": "Dr. Brown",
            "specialization": "Dermatology",
            "active": True,
        },
    ).json()

    start_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    resp = client.post(
        "/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "start_time": start_time,
            "duration_minutes": 30,
        },
    )
    assert resp.status_code == 201
    assert resp.json()["duration_minutes"] == 30


def test_reject_past_appointment():
    patient = client.post(
        "/patients",
        json={
            "first_name": "Bob",
            "last_name": "Marley",
            "email": "bob@example.com",
            "phone": "5559876543",
        },
    ).json()
    doctor = client.post(
        "/doctors",
        json={
            "full_name": "Dr. Green",
            "specialization": "Neurology",
            "active": True,
        },
    ).json()

    past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    resp = client.post(
        "/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "start_time": past_time,
            "duration_minutes": 30,
        },
    )
    assert resp.status_code == 400


def test_reject_overlapping_appointment():
    patient = client.post(
        "/patients",
        json={
            "first_name": "Charlie",
            "last_name": "Day",
            "email": "charlie@example.com",
            "phone": "5551112222",
        },
    ).json()
    doctor = client.post(
        "/doctors",
        json={
            "full_name": "Dr. White",
            "specialization": "Orthopedics",
            "active": True,
        },
    ).json()

    start_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    client.post(
        "/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "start_time": start_time,
            "duration_minutes": 60,
        },
    )

    resp = client.post(
        "/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "start_time": start_time,
            "duration_minutes": 30,
        },
    )
    assert resp.status_code == 409


def test_list_appointments_by_date():
    today = datetime.now(timezone.utc).date().isoformat()
    resp = client.get(f"/appointments?date={today}")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_invalid_date_format():
    resp = client.get("/appointments?date=31-01-2026")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid date format, use YYYY-MM-DD"


# ---------------- SERVICE LAYER TESTS ----------------
@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_patient_service_create_and_get(db):
    patient_in = PatientCreate(
        first_name="Service",
        last_name="User",
        email="service@example.com",
        phone="1234567890",
    )
    patient = patient_service.create_patient(db, patient_in)
    assert patient.id is not None
    fetched = patient_service.get_patient(db, patient.id)
    assert fetched.email == "service@example.com"


def test_doctor_service_create_and_get(db):
    doctor_in = DoctorCreate(
        full_name="Dr. Service", specialization="Cardiology", active=True
    )
    doctor = doctor_service.create_doctor(db, doctor_in)
    assert doctor.id is not None
    fetched = doctor_service.get_doctor(db, doctor.id)
    assert fetched.full_name == "Dr. Service"


def test_appointment_service_create(db):
    patient_in = PatientCreate(
        first_name="App",
        last_name="Tester",
        email="apptester@example.com",
        phone="5555555555",
    )
    patient = patient_service.create_patient(db, patient_in)

    doctor_in = DoctorCreate(
        full_name="Dr. Service", specialization="Dermatology", active=True
    )
    doctor = doctor_service.create_doctor(db, doctor_in)

    start_time = datetime.now(timezone.utc) + timedelta(hours=1)
    appt_in = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_time=start_time,
        duration_minutes=30,
    )
    appt = appointment_service.create_appointment(db, appt_in)
    assert appt.id is not None
    assert appt.doctor_id == doctor.id
    assert appt.patient_id == patient.id
