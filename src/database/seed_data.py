"""
Seed script — generates 100 rows of realistic sample data for every table
in models.py (patients, doctors, appointment_slots, appointments,
medical_records, call_logs), respecting foreign keys and unique constraints.

Usage:
    python -m src.database.seed_data   (or wherever you place this file)

Requires:
    pip install faker sqlalchemy asyncpg

Written async to match base_engine.py's AsyncSession / async_sessionmaker setup.
"""

import asyncio
import sys

if sys.platform == "win32":
    # psycopg's async mode needs SelectorEventLoop; Windows defaults to
    # ProactorEventLoop, which raises "Psycopg cannot use the
    # 'ProactorEventLoop' to run in async mode".
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import random
import uuid
from datetime import date, datetime, timedelta, time as dtime

from faker import Faker
from src.utils.logger_exceptions import get_logger

fake = Faker()
Faker.seed(42)
random.seed(42)

DRY_RUN = False  # set True to preview without touching the DB
logger = get_logger(__name__)

logger.info("Starting data seeding...")

N_PATIENTS = 100
N_DOCTORS = 100
N_APPOINTMENTS = 100
# extra slots so not every slot gets booked (mirrors real availability)
N_SLOTS = 140

SPECIALIZATIONS = [
    "Cardiology", "Dermatology", "Pediatrics", "Orthopedics", "Neurology",
    "General Medicine", "ENT", "Gynecology", "Psychiatry", "Ophthalmology",
    "Gastroenterology", "Endocrinology", "Pulmonology", "Urology", "Oncology",
]
DEPARTMENTS = [
    "Outpatient", "Inpatient", "Emergency", "Surgery", "Diagnostics",
]
QUALIFICATIONS = ["MBBS, MD", "MBBS, MS", "MBBS, DM", "MBBS, MCh", "MBBS, DNB"]

INTENTS = [
    "book_appointment", "reschedule_appointment", "cancel_appointment",
    "check_appointment_status", "doctor_availability", "general_faq",
    "prescription_refill_query", "billing_query",
]

BOOKING_REASONS = [
    "Follow-up consultation", "New patient checkup", "Persistent headache",
    "Annual physical", "Skin rash evaluation", "Chest pain", "Fever and cough",
    "Post-surgery review", "Vaccination", "Routine blood work review",
]

DIAGNOSES = [
    "Hypertension", "Type 2 Diabetes Mellitus", "Acute bronchitis",
    "Migraine", "Seasonal allergic rhinitis", "Gastroenteritis",
    "Lower back strain", "Viral fever", "Mild anemia", "Anxiety disorder",
]

TREATMENTS = [
    "Prescribed medication and advised follow-up in 2 weeks.",
    "Recommended rest, hydration, and OTC symptom relief.",
    "Referred to specialist for further evaluation.",
    "Physical therapy exercises prescribed.",
    "Dosage adjusted; recheck in 1 month.",
    "Lifestyle and dietary counseling provided.",
]

logger.info("Constants and sample data lists initialized.")


def random_time_slot():
    """Return (start_time, end_time) as 30-min slots between 09:00-17:00."""
    start_hour = random.randint(9, 16)
    start_minute = random.choice([0, 30])
    start = dtime(start_hour, start_minute)
    end_minute = start_minute + 30
    end_hour = start_hour
    if end_minute == 60:
        end_minute = 0
        end_hour += 1
    end = dtime(end_hour, end_minute)
    return start, end


def build_data():
    from src.database.models import (
        Patient, Doctor, AppointmentSlot, Appointment, AppointmentStatus,
        MedicalRecord, CallLog, CallOutcome,
    )
    logger.info("Building sample data for patients, doctors, slots, appointments, medical records, and call logs...")

    # ---------- Patients ----------
    patients = []
    for _ in range(N_PATIENTS):
        dob = fake.date_of_birth(minimum_age=1, maximum_age=95)
        patients.append(
            Patient(
                id=uuid.uuid4(),
                full_name=fake.name(),
                gender=random.choice(["Male", "Female", "Other"]),
                date_of_birth=dob,
                phone_number=fake.numerify("+91##########"),
                email=fake.unique.email() if random.random() > 0.15 else None,
            )
        )
    logger.info(f"Generated {len(patients)} patients.")

    # ---------- Doctors ----------
    doctors = []
    logger.info(f"Generating {N_DOCTORS} doctors...")
    for _ in range(N_DOCTORS):
        doctors.append(
            Doctor(
                id=uuid.uuid4(),
                doctor_name="Dr. " + fake.name(),
                specialization=random.choice(SPECIALIZATIONS),
                department=random.choice(DEPARTMENTS),
                qualifications=random.choice(QUALIFICATIONS),
                experience=random.randint(1, 35),
                status=random.random() > 0.05,  # ~95% active
            )
        )
    logger.info(f"Generated {len(doctors)} doctors.")

    # ---------- Appointment Slots ----------
    logger.info(f"Generating up to {N_SLOTS} appointment slots...")
    slots = []
    seen_keys = set()
    today = date.today()
    attempts = 0
    while len(slots) < N_SLOTS and attempts < N_SLOTS * 10:
        attempts += 1
        doctor = random.choice(doctors)
        slot_date = today + timedelta(days=random.randint(-30, 30))
        start, end = random_time_slot()
        key = (doctor.id, slot_date, start)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        slots.append(
            AppointmentSlot(
                id=uuid.uuid4(),
                doctor_id=doctor.id,
                doctor=doctor,
                slot_date=slot_date,
                start_time=start,
                end_time=end,
                is_available=True,
            )
        )
    logger.info(f"Generated {len(slots)} appointment slots.")

    # ---------- Appointments (books N_APPOINTMENTS distinct slots) ----------
    logger.info(f"Booking up to {N_APPOINTMENTS} appointments from available slots...")
    booked_slots = random.sample(slots, min(N_APPOINTMENTS, len(slots)))
    appointments = []
    statuses = list(AppointmentStatus)
    for slot in booked_slots:
        slot.is_available = False
        patient = random.choice(patients)
        status = random.choices(
            statuses,
            weights=[15, 15, 40, 15, 10, 5],  # skew toward COMPLETED
            k=1,
        )[0]
        appointments.append(
            Appointment(
                id=uuid.uuid4(),
                patient_id=patient.id,
                patient=patient,
                doctor_id=slot.doctor_id,
                doctor=slot.doctor,
                appointment_slot_id=slot.id,
                slot=slot,
                appointment_status=status,
                booking_reason=random.choice(BOOKING_REASONS),
                created_at=datetime.now() - timedelta(days=random.randint(0, 45)),
            )
        )
    logger.info(f"Booked {len(appointments)} appointments.")

    # ---------- Medical Records (only for COMPLETED appointments) ----------
    logger.info("Generating medical records for completed appointments...")
    medical_records = []
    for appt in appointments:
        if appt.appointment_status == AppointmentStatus.COMPLETED:
            treatment_dt = datetime.now() - timedelta(days=random.randint(0, 30))
            follow_up = (
                treatment_dt + timedelta(days=random.choice([7, 14, 30, 90]))
                if random.random() > 0.4 else None
            )
            medical_records.append(
                MedicalRecord(
                    id=uuid.uuid4(),
                    appointment_id=appt.id,
                    appointment=appt,
                    patient_id=appt.patient_id,
                    patient=appt.patient,
                    doctor_id=appt.doctor_id,
                    doctor=appt.doctor,
                    diagnosis=random.choice(DIAGNOSES),
                    treatment=random.choice(TREATMENTS),
                    treatment_date=treatment_dt,
                    follow_up_date=follow_up,
                    notes=fake.sentence(nb_words=12) if random.random() > 0.5 else None,
                )
            )
    logger.info(f"Generated {len(medical_records)} medical records.")

    # ---------- Call Logs ----------
    logger.info("Generating call logs for patients and appointments...")
    call_logs = []
    outcomes = list(CallOutcome)
    for _ in range(100):
        # ~80% of calls resolve to a known patient / appointment
        linked = random.random() > 0.2
        patient = random.choice(patients) if linked else None
        appt = random.choice(appointments) if linked and random.random() > 0.3 else None
        started = datetime.now() - timedelta(
            days=random.randint(0, 60), minutes=random.randint(0, 1440)
        )
        duration = random.randint(20, 480)  # seconds
        outcome = random.choices(
            outcomes,
            weights=[55, 15, 15, 5, 10],  # RESOLVED, ESCALATED, ABANDONED, VOICEMAIL, FAILED
            k=1,
        )[0]
        call_logs.append(
            CallLog(
                id=uuid.uuid4(),
                patient_id=patient.id if patient else None,
                patient=patient,
                appointment_id=appt.id if appt else None,
                appointment=appt,
                caller_phone=patient.phone_number if patient else fake.numerify("+91##########"),
                call_provider_id=f"CA{uuid.uuid4().hex[:24]}",
                started_at=started,
                ended_at=started + timedelta(seconds=duration) if outcome != CallOutcome.ABANDONED else None,
                duration_seconds=duration if outcome != CallOutcome.ABANDONED else random.randint(3, 15),
                intent=random.choice(INTENTS),
                outcome=outcome,
                transcript=fake.paragraph(nb_sentences=4),
                recording_url=f"https://recordings.example.com/{uuid.uuid4()}.mp3",
                call_metadata={
                    "stt_confidence": round(random.uniform(0.75, 0.99), 2),
                    "language": "en-IN",
                    "sentiment": random.choice(["positive", "neutral", "negative"]),
                },
            )
        )
    logger.info(f"Generated {len(call_logs)} call logs.")

    return patients, doctors, slots, appointments, medical_records, call_logs


async def main():
    logger.info("Starting main seeding process...")
    patients, doctors, slots, appointments, medical_records, call_logs = build_data()

    print(f"Generated: {len(patients)} patients, {len(doctors)} doctors, "
          f"{len(slots)} slots, {len(appointments)} appointments, "
          f"{len(medical_records)} medical_records, {len(call_logs)} call_logs")

    if DRY_RUN:
        print("DRY_RUN=True — not writing to DB. Sample patient:", patients[0].full_name)
        return

    # Adjust this import if your session factory lives elsewhere.
    from src.database.base_engine import AsyncSessionLocal

    logger.info("Creating database session...")
    async with AsyncSessionLocal() as session:
        try:
            session.add_all(patients)
            session.add_all(doctors)
            await session.flush()  # assigns/validates FK targets before slots/appointments
            session.add_all(slots)
            await session.flush()
            session.add_all(appointments)
            await session.flush()
            session.add_all(medical_records)
            session.add_all(call_logs)
            await session.commit()
            logger.info("Seed data committed successfully.")
        except Exception:
            await session.rollback()
            logger.error("Error occurred while committing seed data.")
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(main())