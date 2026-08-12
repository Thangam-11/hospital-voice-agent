import pytest
from datetime import date
from uuid import uuid4

from src.agents_layer.tools.appointment_tools import create_appointment_tools


class FakePatient:
    id = uuid4()
    full_name = "John Doe"


class FakePatientService:

    async def find_by_name_and_dob(
        self,
        full_name: str,
        date_of_birth: date,
    ):
        if (
            full_name == "John Doe"
            and date_of_birth == date(1990, 1, 1)
        ):
            return FakePatient()

        return None


class FakeAppointmentService:
    pass


class FakeSlot:
    def __init__(self):
        self.id = uuid4()
        self.doctor_id = uuid4()
        self.slot_date = date(2026, 8, 15)
        self.start_time = "10:00"
        self.end_time = "10:30"


class FakeAppointmentServiceWithSlots:

    async def find_available_slots(
        self,
        specialization=None,
        date_from=None,
        limit=10,
    ):
        return [FakeSlot()]


class FakeAppointment:
    def __init__(self):
        self.id = uuid4()
        self.doctor_id = uuid4()
        self.appointment_slot_id = uuid4()

        class Status:
            value = "SCHEDULED"

        self.appointment_status = Status()


class FakeAppointmentServiceForBooking:

    async def book_appointment(
        self,
        patient_id,
        slot_id,
        reason=None,
    ):
        return FakeAppointment()



@pytest.mark.asyncio
async def test_verify_patient_success():

    patient_service = FakePatientService()
    appointment_service = FakeAppointmentService()

    tools = create_appointment_tools(
        service=appointment_service,
        patient_service=patient_service,
    )

    verify_patient = tools[0]

    tool_call = {
        "name": "verify_patient",
        "args": {
            "full_name": "John Doe",
            "date_of_birth": "1990-01-01",
        },
        "id": "test-call-001",
        "type": "tool_call",
    }

    result = await verify_patient.ainvoke(tool_call)

    print(result)

    assert result is not None

@pytest.mark.asyncio
async def test_verify_patient_not_found():

    patient_service = FakePatientService()
    appointment_service = FakeAppointmentService()

    tools = create_appointment_tools(
        service=appointment_service,
        patient_service=patient_service,
    )

    verify_patient = tools[0]

    tool_call = {
        "name": "verify_patient",
        "args": {
            "full_name": "Unknown Patient",
            "date_of_birth": "1990-01-01",
        },
        "id": "test-call-002",
        "type": "tool_call",
    }

    result = await verify_patient.ainvoke(tool_call)

    print(result)

    assert result is not None


@pytest.mark.asyncio
async def test_find_available_slots_success():

    patient_service = FakePatientService()
    appointment_service = FakeAppointmentServiceWithSlots()

    tools = create_appointment_tools(
        service=appointment_service,
        patient_service=patient_service,
    )

    find_available_slots = tools[1]

    tool_call = {
        "name": "find_available_slots",
        "args": {
            "specialization": "Cardiology",
            "date_from": "2026-08-15",
            "limit": 10,
        },
        "id": "test-call-003",
        "type": "tool_call",
    }

    result = await find_available_slots.ainvoke(tool_call)

    print(result)

    assert result is not None
@pytest.mark.asyncio
async def test_book_appointment_success():

    patient_service = FakePatientService()
    appointment_service = FakeAppointmentServiceForBooking()

    tools = create_appointment_tools(
        service=appointment_service,
        patient_service=patient_service,
    )

    tool_node = ToolNode(tools)

    patient_id = uuid4()
    slot_id = uuid4()

    tool_call = {
        "name": "book_appointment",
        "args": {
            "slot_id": str(slot_id),
            "reason": "Regular consultation",
        },
        "id": "test-call-004",
        "type": "tool_call",
    }

    message = AIMessage(
        content="",
        tool_calls=[tool_call],
    )

    result = await tool_node.ainvoke({
        "messages": [message],
        "patient_id": patient_id,
    })

    print(result)

    assert result is not None