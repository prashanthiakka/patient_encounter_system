from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from src.patient_encounter_system.database import Base


class Appointment(Base):
    __tablename__ = "prashanthi_appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("prashanthi_patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("prashanthi_doctors.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    patient = relationship("Patient")
    doctor = relationship("Doctor")

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.duration_minutes)
