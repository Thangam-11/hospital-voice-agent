import uuid
import enum
from datetime import datetime, date, time

from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    Float,
    DateTime,
    Date,
    Time,
    ForeignKey,
    JSON,
    UniqueConstraint,
    Index,
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.database.base import Base  # re-exported for convenience/back-compat


class Patient(Base):
    __tablename__ = "patients"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    full_name = mapped_column(String(255), nullable=False)

    gender = mapped_column(String(20), nullable=True)

    date_of_birth = mapped_column(Date, nullable=False)

    # Not unique anymore — a household/family often shares one phone line,
    # and multiple patient records can legitimately share a number.
    phone_number = mapped_column(String(20), nullable=False, index=True)

    # Optional: phone-first intake means many callers won't have/give an email.
    email = mapped_column(String(255), unique=True, nullable=True)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    appointments = relationship("Appointment", back_populates="patient")

    medical_records = relationship("MedicalRecord", back_populates="patient")

    call_logs = relationship("CallLog", back_populates="patient")

    __table_args__ = (
        # Natural verification pair for a voice agent: "confirm your phone and date of birth"
        Index("ix_patients_phone_dob", "phone_number", "date_of_birth"),
    )


class Doctor(Base):
    __tablename__ = "doctors"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    doctor_name = mapped_column(String(255), nullable=False)

    specialization = mapped_column(String(255), nullable=False, index=True)

    department = mapped_column(String(255), nullable=False, index=True)

    qualifications = mapped_column(String(255), nullable=False)

    experience = mapped_column(Integer, nullable=False)

    status = mapped_column(Boolean, default=True)

    appointments = relationship("Appointment", back_populates="doctor")

    slots = relationship("AppointmentSlot", back_populates="doctor")

    medical_records = relationship("MedicalRecord", back_populates="doctor")


class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    doctor_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    slot_date = mapped_column(Date, nullable=False, index=True)

    start_time = mapped_column(Time, nullable=False)

    end_time = mapped_column(Time, nullable=False)

    is_available = mapped_column(Boolean, default=True)

    doctor = relationship("Doctor", back_populates="slots")

    appointment = relationship(
        "Appointment",
        back_populates="slot",
        uselist=False,
    )

    __table_args__ = (
        # Prevents creating two overlapping/duplicate slot rows for the same
        # doctor at the same start time.
        UniqueConstraint(
            "doctor_id", "slot_date", "start_time", name="uq_doctor_slot_start"
        ),
    )


class AppointmentStatus(enum.Enum):
    SCHEDULED = "Scheduled"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    RESCHEDULED = "Rescheduled"
    NO_SHOW = "No Show"


class Appointment(Base):
    __tablename__ = "appointments"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    patient_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    doctor_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    appointment_slot_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointment_slots.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )

    appointment_status = mapped_column(
        SAEnum(AppointmentStatus),
        default=AppointmentStatus.SCHEDULED,
        nullable=False,
        index=True,
    )

    booking_reason = mapped_column(Text)

    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    patient = relationship("Patient", back_populates="appointments")

    doctor = relationship("Doctor", back_populates="appointments")

    slot = relationship("AppointmentSlot", back_populates="appointment")

    medical_record = relationship(
        "MedicalRecord",
        back_populates="appointment",
        uselist=False,
    )

    call_log = relationship(
        "CallLog",
        back_populates="appointment",
        uselist=False,
    )


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    appointment_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    patient_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    doctor_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    diagnosis = mapped_column(Text, nullable=False)

    treatment = mapped_column(Text, nullable=False)

    treatment_date = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    follow_up_date = mapped_column(DateTime(timezone=True))

    notes = mapped_column(Text)

    appointment = relationship(
        "Appointment",
        back_populates="medical_record",
    )

    patient = relationship(
        "Patient",
        back_populates="medical_records",
    )

    doctor = relationship(
        "Doctor",
        back_populates="medical_records",
    )


class CallOutcome(enum.Enum):
    RESOLVED = "Resolved"
    ESCALATED = "Escalated to Human"
    ABANDONED = "Abandoned"
    VOICEMAIL = "Voicemail"
    FAILED = "Failed"


class CallLog(Base):
    """
    Captures every inbound/outbound voice-agent call. This is the table that
    makes the schema an actual *voice agent* project instead of a generic
    clinic scheduling DB — it's also where your analytics/demo queries
    (avg call duration, intent breakdown, escalation rate) will come from.
    """

    __tablename__ = "call_logs"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Nullable — caller may not be identified/matched to a patient record yet
    # (e.g. call dropped during verification, or a first-time caller).
    patient_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    appointment_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    caller_phone = mapped_column(String(20), nullable=False, index=True)

    # External telephony/voice-platform identifier (Twilio Call SID, Vapi
    # call id, etc.) — lets you correlate DB rows back to provider dashboards.
    call_provider_id = mapped_column(String(255), unique=True, nullable=True)

    started_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    ended_at = mapped_column(DateTime(timezone=True), nullable=True)

    duration_seconds = mapped_column(Integer, nullable=True)

    # e.g. "book_appointment", "reschedule", "cancel", "check_status", "faq"
    intent = mapped_column(String(100), nullable=True, index=True)

    outcome = mapped_column(SAEnum(CallOutcome), nullable=True, index=True)

    transcript = mapped_column(Text, nullable=True)

    recording_url = mapped_column(String(500), nullable=True)

    # Free-form bag for anything provider/agent-specific (STT confidence,
    # sentiment score, function-call trace, etc.) without a migration.
    call_metadata = mapped_column(JSON, nullable=True)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="call_logs")

    appointment = relationship("Appointment", back_populates="call_log")

class ActivityLog(Base):
    """
    Centralized application activity/audit history.

    Tracks important events across patients, appointments,
    voice calls, and other hospital operations.
    """

    __tablename__ = "activity_logs"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Example:
    # APPOINTMENT_BOOKED
    # APPOINTMENT_CANCELLED
    # APPOINTMENT_RESCHEDULED
    # PATIENT_REGISTERED
    # PATIENT_VERIFIED
    # CALL_COMPLETED
    # CALL_ESCALATED
    event_type = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Example:
    # appointment
    # patient
    # call
    # doctor
    entity_type = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # ID of the object associated with this event.
    entity_id = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    patient_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    appointment_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Examples:
    # AI_AGENT
    # ADMIN
    # PATIENT
    # DOCTOR
    # SYSTEM
    actor_type = mapped_column(
        String(50),
        nullable=False,
    )

    description = mapped_column(
        Text,
        nullable=True,
    )

    # Extra event-specific information.
    #
    # Python attribute = log_metadata
    # Database column = metadata
    log_metadata = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    patient = relationship(
        "Patient",
        foreign_keys=[patient_id],
    )

    appointment = relationship(
        "Appointment",
        foreign_keys=[appointment_id],
    )