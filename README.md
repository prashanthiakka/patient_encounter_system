
# Medical Encounter Management System (MEMS)

A production-grade Python backend system designed for managing medical encounters at a mid-sized outpatient clinic. This system handles patient registration, doctor management, and appointment scheduling with strict enforcement of healthcare business rules and timezone-aware data integrity.

## 🚀 Features

-   **Patient Management**: Create and retrieve patient records with email uniqueness enforcement.
-   **Doctor Management**: Support for active/inactive status and specialized care providers.
-   **Smart Scheduling**: 
    -   Prevents overlapping appointments for the same doctor.
    -   Rejects appointments scheduled in the past.
    -   Enforces duration constraints (15–180 minutes).
-   **Timezone-Aware**: All datetime handling uses UTC/timezone-aware objects to ensure global consistency.
-   **Production Infrastructure**: Automated CI/CD pipeline, linting, formatting, and security scanning.

## 🛠️ Tech Stack

-   **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
-   **Database**: MySQL (hosted on `cp-15.webhostbox.net`)
-   **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
-   **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/)
-   **Dependency Management**: [Poetry](https://python-poetry.org/)
-   **CI/CD**: GitHub Actions (Ruff, Black, Bandit, Pytest)

## 📁 Project Structure

```text
patient-encounter-system/
├── src/
│   ├── main.py          # FastAPI application & endpoints
│   ├── database.py      # SQLAlchemy engine & session config
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic validation schemas
│   ├── services/        # Business logic & overlap detection
│   └── reset_db.py      # Database initialization script
├── tests/               # Pytest suite (80%+ coverage)
├── .github/workflows/   # CI/CD Pipeline configuration
├── pyproject.toml       # Poetry dependencies
└── README.md

```

## ⚙️ Setup & Installation

### 1. Prerequisites

* Python 3.10+
* Poetry (`pip install poetry`)

### 2. Install Dependencies

```bash
poetry install

```

### 3. Initialize Database

This command will drop existing tables (prefixed with `sivapriya_`) and recreate them with the correct schema.

```bash
poetry run python -m src.reset_db

```

### 4. Run the Application

```bash
poetry run uvicorn src.main:app --reload

```

The API will be available at: `http://127.0.0.1:8000`
Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

## 🧪 Testing & Quality

Run the test suite with coverage reporting:

```bash
# Must have PYTHONPATH set to root
$env:PYTHONPATH = "."
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

```

## 📡 API Contracts

### Patients

* `POST /patients`: Register a new patient.
* `GET /patients/{id}`: Retrieve patient details.

### Doctors

* `POST /doctors`: Register a new doctor.
* `GET /doctors/{id}`: Retrieve doctor details.

### Appointments

* `POST /appointments`: Schedule an encounter. Validates overlaps and duration.
* `GET /appointments?date=YYYY-MM-DD`: List all appointments for the clinic on a specific date.
* `GET /appointments?date=YYYY-MM-DD&doctor_id=1`: List appointments for a specific doctor.

## 🛡️ Domain Rules enforced

1. **Overlaps**: Doctors cannot be double-booked.
2. **Future-only**: Appointments cannot be set in the past.
3. **Duration**: Must be between 15 and 180 minutes.
4. **Integrity**: Records with existing appointments cannot be deleted.



